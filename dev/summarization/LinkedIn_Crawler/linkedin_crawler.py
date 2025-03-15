# %%
def scrape_linkedin(scroll_count=10, save_csv=True, save_json=True):
    import time
    import csv
    import os
    import requests
    import re
    import json
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.edge.options import Options as EdgeOptions
    from dotenv import load_dotenv
    import pathlib

    current_dir = pathlib.Path(__file__).parent.absolute()
    env_path = current_dir / '.env'
    load_dotenv(dotenv_path=env_path)

    USERNAME = os.getenv('LINKEDIN_USERNAME')
    if not USERNAME:
        raise ValueError("환경 변수에 LINKEDIN_USERNAME이 설정되어 있지 않습니다.")
    PASSWORD = os.getenv('LINKEDIN_PASSWORD')
    if not PASSWORD:
        raise ValueError("환경 변수에 LINKEDIN_PASSWORD가 설정되어 있지 않습니다.")

    os.makedirs('linkedin_images', exist_ok=True)

    csv_filename = "linkedin_posts.csv"
    json_filename = "linkedin_posts.json"
    existing_posts = set()
    
    if save_csv and os.path.exists(csv_filename):
        with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_posts.add((row['Name'], row['Content']))
                
    if save_json and os.path.exists(json_filename):
        with open(json_filename, 'r', encoding='utf-8') as jsonfile:
            try:
                json_data = json.load(jsonfile)
                for row in json_data:
                    existing_posts.add((row.get('Name', ''), row.get('Content', '')))
            except Exception:
                pass

    edge_options = EdgeOptions()
    edge_options.use_chromium = True
    edge_options.add_argument("--headless=new")
    edge_options.add_argument("--disable-gpu")

    driver = webdriver.Edge(options=edge_options)

    try:
        print("LinkedIn 로그인 페이지에 접속 중...")
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)

        username_field = driver.find_element("id", "username")
        password_field = driver.find_element("id", "password")
        username_field.send_keys(USERNAME)
        password_field.send_keys(PASSWORD)
        password_field.send_keys(Keys.RETURN)
        time.sleep(3)

        print("피드 페이지로 이동 중...")
        driver.get("https://www.linkedin.com/feed/")
        time.sleep(3)

        scroll_pause_time = 2
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(scroll_count):
            print(f"스크롤 {i+1}/{scroll_count} 진행 중...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                for attempt in range(3):
                    print(f"높이 변화 없음 - 재시도 {attempt+1}/3...")
                    time.sleep(2)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height != last_height:
                        break
                if new_height == last_height:
                    print("더 이상 스크롤 할 내용이 없습니다.")
                    break
            last_height = new_height

        posts = driver.find_elements("css selector", "div.feed-shared-update-v2")
        print(f"총 {len(posts)}개의 게시글 발견됨.")

        new_data = []
        current_max_id = len(existing_posts)

        for post_idx, post in enumerate(posts, start=1):
            print(f"게시글 {post_idx} 처리 중...")
            try:
                meta_link = post.find_element("css selector", "a.update-components-actor__meta-link")
                name_element = meta_link.find_element("css selector", "span.update-components-actor__title span[aria-hidden='true']")
                name = name_element.text.strip()
            except Exception:
                name = "Unknown"

            content = ""
            try:
                content_elements = post.find_elements("css selector", "span.break-words")
                content = " ".join([elem.text.strip() for elem in content_elements if elem.text.strip()])
            except Exception:
                content = ""

            post_key = (name, content)
            if post_key in existing_posts:
                print(f"게시글 {post_idx}는 이미 존재하여 건너뜁니다.")
                continue

            image_files = []
            try:
                sanitized_name = re.sub(r'[\\/*?:"<>| ]', '_', name)[:50]
                post_id = current_max_id + post_idx

                carousel_elements = post.find_elements("css selector", "li.carousel-slide")
                if carousel_elements:
                    for img_idx, element in enumerate(carousel_elements):
                        try:
                            img = element.find_element("css selector", "img")
                            url = img.get_attribute("data-src") or img.get_attribute("src")
                            if url:
                                filename = f"{post_id}_{sanitized_name}_{img_idx}.jpg"
                                filepath = os.path.join('linkedin_images', filename)

                                if not os.path.exists(filepath):
                                    response = requests.get(url, timeout=10)
                                    if response.status_code == 200:
                                        with open(filepath, 'wb') as f:
                                            f.write(response.content)
                                image_files.append(filename)
                        except Exception:
                            continue
                else:
                    try:
                        img = post.find_element("css selector", "div.update-components-image__container-wrapper img")
                        url = img.get_attribute("src")
                        if url:
                            filename = f"{post_id}_{sanitized_name}_0.jpg"
                            filepath = os.path.join('linkedin_images', filename)

                            if not os.path.exists(filepath):
                                response = requests.get(url, timeout=10)
                                if response.status_code == 200:
                                    with open(filepath, 'wb') as f:
                                        f.write(response.content)
                            image_files.append(filename)
                    except Exception:
                        pass
            except Exception:
                pass

            new_data.append({
                "ID": current_max_id + post_idx,
                "Name": name,
                "Content": content,
                "Image": ", ".join([os.path.join('linkedin_images', img) for img in image_files])
            })
            print(f"새 게시글 {post_idx} 수집 완료: {name}")

        if new_data:
            if save_csv:
                file_exists = os.path.exists(csv_filename)
                with open(csv_filename, 'a', newline='', encoding="utf-8-sig") as csvfile:
                    fieldnames = ["ID", "Name", "Content", "Image"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    if not file_exists:
                        writer.writeheader()
                    writer.writerows(new_data)

            if save_json:
                if os.path.exists(json_filename):
                    with open(json_filename, 'r', encoding="utf-8") as jf:
                        try:
                            json_data = json.load(jf)
                        except Exception:
                            json_data = []
                else:
                    json_data = []

                existing_json_posts = {(item.get("Name", ""), item.get("Content", "")) for item in json_data}
                for item in new_data:
                    if (item["Name"], item["Content"]) not in existing_json_posts:
                        json_data.append(item)

                with open(json_filename, 'w', encoding="utf-8") as jf:
                    json.dump(json_data, jf, ensure_ascii=False, indent=4)

            save_message = []
            if save_csv:
                save_message.append("CSV")
            if save_json:
                save_message.append("JSON")
            save_formats = " 및 ".join(save_message)
            print(f"총 {len(new_data)}개의 새 게시글이 {save_formats} 파일에 추가 저장되었습니다. 이미지는 linkedin_images 폴더에 저장되었습니다.")
        else:
            print("추가할 새 게시글이 없습니다.")
    finally:
        driver.quit()

if __name__ == "__main__":
    try:
        scroll_count = 3
        scrape_linkedin(scroll_count=scroll_count, save_csv=False, save_json=True)
    except Exception as e:
        print(f"오류 발생: {e}")
# %%
