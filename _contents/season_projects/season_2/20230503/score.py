import cv2
from PIL import Image
import matplotlib.pyplot as plt
import easyocr
import pickle
from PIL import Image, ImageDraw, ImageFont
import torch
from sklearn.metrics.pairwise import cosine_similarity

###############
answers = []
OCR_answers = []
LLM_answers = []
proposed_LLM_answers = []
###############

# 문장 데이터
file_path0 = "data/data_sents.pickle" 
with open(file_path0, "rb") as file:
    data_sents = pickle.load(file)

# print(data_sents)

for i in range(len(data_sents)):
    sent = data_sents[i]
    for j in range(len(sent)):
        sent[j] = sent[j].lower()

# print(data_sents)


# 각 문장에서 mask가 된 단어의 순서
file_path1 = "data/data.pickle" 
with open(file_path1, "rb") as file:
    data = pickle.load(file)

# OCR 결과
file_path2 = "data/OCR_results.pickle" 
with open(file_path2, "rb") as file:
    OCR_results = pickle.load(file)

# LLM 결과
file_path3 = "data/LLM_results.pickle" 
with open(file_path3, "rb") as file:
    LLM_results = pickle.load(file)


numbers = []
for i in range(len(LLM_results)):
# for i in range(3):
    # number: 문장의 순번 (중간에 누락된 경우도 있어 따로 표시함)
    number = LLM_results[i][0]
    numbers.append(number)

    # order: 해당 문장의 mask token의 순서
    order = data[number]

    # 정답지
    answers.append(data_sents[number][order])
    # OCR 답지
    OCR_answers.append(OCR_results[number][1:][0][order][1])

    tmp = []

    for j in range(len(LLM_results[i][1:][0])):
        
        predicted_word = LLM_results[i][1:][0][j]["token_str"].lower()
        probability = LLM_results[i][1:][0][j]["score"]
        tmp.append((predicted_word, probability))

    # print(tmp)

    # LLM 답지
    LLM_answers.append(tmp)


    # 해당 문장순번의 이미지 
    image = cv2.imread('data/noise_text/noise_image' + str(number) + '.png')

    reader = easyocr.Reader(['en'])
    result = reader.readtext(image, detail = 1, paragraph = False)

    coord, text, prob = result[order][0], result[order][1], result[order][2]

    print('===========' + str(i) + '=============')
    # print(number)     # 문장의 순번
    # print(order)      # 해당 문장의 mask token의 index
    print(data_sents[number][order])    # masking된 문자의 원래문자
    # print(coord)      # mask token의 위치
    # print(tmp)        # 
    # print(text)
    # print(prob)


    (topleft, topright, bottomright, bottomleft) = coord
    tx,ty = (int(topleft[0]), int(topleft[1]))
    bx,by = (int(bottomright[0]), int(bottomright[1]))
    x = abs(tx - bx)
    y = abs(ty - by)

    # 문장의 mask된 부분을 잘라서 저장
    region = image[0:100, tx:tx+x]
    cv2.imwrite('data/target.png', region)

    """
    후보군 이미지 저장
    """
    texts = []
    probs = []
    for k in range(len(tmp)):

        text = tmp[k][0]
        prob = tmp[k][1]

        texts.append(text)
        probs.append(prob)

        # Set the font properties
        font_size = 100
        font_color = (0, 0, 0)  # RGB color tuple
        font_path = "/home/moonstar/python/NLP/OCR/Roboto/Roboto-Regular.ttf"  # Replace with the path to your desired font file

        # Set the image size based on the text length and font size
        image_width = len(text) * int(font_size/2)
        image_height = font_size
        image_size = (image_width, image_height)

        # Create a blank image with a white background
        image = Image.new("RGB", image_size, "white")
        draw = ImageDraw.Draw(image)

        # Load the font
        font = ImageFont.truetype(font_path, font_size)

        # Calculate the bounding box of the text
        text_bbox = draw.textbbox((0, 0), text, font=font)

        # Calculate the position to center the text
        text_x = (image_width - text_bbox[2]) // 2
        text_y = (image_height - text_bbox[3]) // 2

        # Draw the text on the image
        draw.text((text_x, text_y), text, font=font, fill=font_color)

        # Save the image
        image.save("data/candidate_text/candidate_image" + str(k) + ".png")


    # print('========= text and prob =========')
    # print(texts)
    # print(probs)
    mean = sum(probs)/len(probs)
    # print(mean)
    
    high_prob_texts = []
    high_probs = []

    for prob in probs:

        if prob >= mean:
            index = probs.index(prob)
            high_prob_texts.append(texts[index])
            high_probs.append(probs[index])


    """
    후보군 이미지 평가
    """
    similarities = []

    for l in range(len(high_prob_texts)):
        imageA = cv2.imread('data/target.png')
        imageB = cv2.imread("data/candidate_text/candidate_image" + str(l) + ".png")

        # 패딩
        imageA = torch.tensor(imageA)
        imageB = torch.tensor(imageB)

        imageA = imageA.reshape(1, -1)
        imageB = imageB.reshape(1, -1)

        # print(imageA.shape)
        # print(imageB.shape)

        A = imageA.shape[1]
        B = imageB.shape[1]

        images = [imageA, imageB]
        tmp2 = [A, B]
        big = max(tmp2)
        big_index = tmp2.index(big)
        small = min(tmp2)
        small_index = tmp2.index(small)

        # print(big)
        # print(big_index)

        imageA = imageA[0][:big]
        imageB = imageB[0][:big]

        add = torch.tensor([[0 for i in range(abs(A-B))]])

        images[small_index] = torch.cat((images[small_index], add), dim=-1)

        imageA = images[0]
        imageB = images[1]

        # print(imageA)
        # print(imageB)
        # print(imageA.shape)
        # print(imageB.shape)


        sim = cosine_similarity(imageA, imageB).tolist()
        similarities.append(sim)


    # print('========         =========')
    # print(high_prob_texts)
    # print(high_probs)
    # print(similarities)


    # 1. OCR detecting 정확도
    # 2. LLM 모델 정확도
    # 위 두가지 경우를 모두 곱하여 최종 스코어 계산
    
    scores = []
    score = 0
    for i in range(len(high_prob_texts)):
        score = high_probs[i] * similarities[i][0][0]
        scores.append(score)

    # print(scores)

    max_sim = max(scores)
    max_sim_index = scores.index(max_sim)
    max_token = high_prob_texts[max_sim_index]

    print('00000000000000')
    print(max_token)

    proposed_LLM_answers.append(max_token)



OCR_score = 0
LLM_score1 = 0
LLM_score2 = 0
proposed_LLM_score = 0

for i in range(len(numbers)):

    # if answers[i] != '.':
    #     answers[i] = answers[i].lower()
    # if OCR_answers[i] != '.': 
    #     OCR_answers[i] = OCR_answers[i].lower()
    # if LLM_answers[i][0][0] != '.':
    #     LLM_answers[i][0][0] = LLM_answers[i][0][0].lower()
    # if proposed_LLM_answers[i] != '.':
    #     proposed_LLM_answers[i] = proposed_LLM_answers[i].lower()

    if answers[i] == OCR_answers[i]:
        OCR_score += 1
    
    # LLM argmax
    if answers[i] == LLM_answers[i][0][0]:
        LLM_score1 += 1

    # LLM answer에 포함 되기만 하면 
    llm = []
    for word in LLM_answers[i]:
        # if word[0] != '.':
        #     word[0] = word[0].lower()
        llm.append(word[0])

    if answers[i] in llm:
        LLM_score2 += 1

    if answers[i] == proposed_LLM_answers[i]:
        proposed_LLM_score += 1





print('========= Score ========')
print(OCR_score / len(numbers))
print(LLM_score1 / len(numbers))
print(LLM_score2 / len(numbers))
print(proposed_LLM_score / len(numbers))

print(LLM_score1 / OCR_score)
print(LLM_score2 / OCR_score)
print(proposed_LLM_score / OCR_score)

