from PIL import Image, ImageDraw, ImageFont
import nltk
import re
import pickle

##############
k = 200000
max_len = 20
min_len = 3
##############

# nltk.download('punkt')  # Download the necessary resource (only required once)

# 텍스트 파일 불러오기
# """
# http://qwone.com/~jason/20Newsgroups/
# """
# file_path = "/home/moonstar/python/NLP/OCR/data/20news-19997/20_newsgroups/sci.electronics/52729" 

# with open(file_path, 'r') as file:
#     data = file.read()


# print(data)
# print(data[0:10])
# print(data[1])

"""
https://www.kaggle.com/datasets/jayashree4/fiction
"""
file_path = "/home/moonstar/python/NLP/OCR/data/fiction_data/fiction_data.txt"

with open(file_path, 'r') as file:
    data = file.read()


print(data)

new_data = data

def remove_special_characters(text):
    # Remove punctuation and special characters
    # cleaned_text = re.sub(r'[@,:''``''-]', '', text)
    cleaned_text = re.sub(r'[^\w\s]', '', text)
    # cleaned_text = re.sub(r'[0-9]', '', cleaned_text)
    return cleaned_text

data = remove_special_characters(new_data)
print(data)

new_data = []
t = 0
for i in data:
    if i == ' ':
        new_data.append('       ')
    elif i == '\n' and j != '\n' and t > 0:
        new_data.append('.      ')
    else:
        new_data.append(i)

    j = i
    t += 1
    
new_data = ''.join(new_data)
print(new_data)

# Tokenize the sentence
# tokens = nltk.word_tokenize(sentence)
# new_data = data
sentences = nltk.sent_tokenize(new_data)
print(sentences)

# print('000000000000000')
# print(len(sentences[0]))
# print(sentences[0])
# print('11111111111')
# print(len(sentences))
sentences.pop()
# print(sentences)
# print(len(sentences))

sentences = sentences[:2000]
print(len(sentences))
# print(sentences[0])

new_data2 = []
data_sents = []
t = 0
for sentence in sentences:
    tmp = []
    sent = ''
    tokens = nltk.word_tokenize(sentence)

    if len(tokens) <= max_len and len(tokens) >= min_len:
        for token in tokens:
            if token == '.':
                pass
            else:
                token = token.lower()
                sent += '       ' + token
        new_data2.append(sent)
        data_sents.append(tokens)

    

# # print(new_data2)
print('========== Number of sentences =========')
print(len(new_data2))
# print(new_data2)
print(len(data_sents))
# print(data_sents)

# data1 = data_sents
# file_path1 = "data/data_sents_fiction.pickle"  # Specify the file path and name
# with open(file_path1, "wb") as file:
#     # Write the data to the file using pickle.dump()
#     pickle.dump(data1, file)

# # Define the text to be converted into an image
# # text = "Hello, World!"
# print('==============')
# # text = sentences[0][:50]
# texts = new_data2
# print(texts)
# print(len(texts))

# for i in range(len(texts)):

#     text = texts[i]

#     # Set the font properties
#     font_size = 100
#     font_color = (0, 0, 0)  # RGB color tuple
#     font_path = "/home/moonstar/python/NLP/OCR/Roboto/Roboto-Regular.ttf"  # Replace with the path to your desired font file

#     # Set the image size based on the text length and font size
#     image_width = len(text) * int(font_size/2)
#     image_height = font_size
#     image_size = (image_width, image_height)

#     # Create a blank image with a white background
#     image = Image.new("RGB", image_size, "white")
#     draw = ImageDraw.Draw(image)

#     # Load the font
#     font = ImageFont.truetype(font_path, font_size)

#     # Calculate the bounding box of the text
#     text_bbox = draw.textbbox((0, 0), text, font=font)

#     # Calculate the position to center the text
#     text_x = (image_width - text_bbox[2]) // 2
#     text_y = (image_height - text_bbox[3]) // 2

#     # Draw the text on the image
#     draw.text((text_x, text_y), text, font=font, fill=font_color)

#     # Save the image
#     image.save("data/original_text_fiction/text_image" + str(i) + ".png")