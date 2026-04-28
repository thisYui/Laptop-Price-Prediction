import requests
from bs4 import BeautifulSoup
import time
import json

def get_product_links(page, config=None):
    """Lấy danh sách link sản phẩm từ trang danh mục."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    }
    url = f"https://www.chotot.com/mua-ban-laptop?page={page}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm các thẻ <a> có class cwv3xk0 theo yêu cầu
        links = []
        a_tags = soup.find_all('a', class_='cwv3xk0')
        for a in a_tags:
            href = a.get('href')
            if href and '.htm' in href:
                # Loại bỏ các tham số theo dõi sau dấu # hoặc ? để có URL sạch
                clean_url = href.split('#')[0].split('?')[0]
                if not clean_url.startswith('http'):
                    clean_url = "https://www.chotot.com" + clean_url
                links.append(clean_url)
        
        return list(set(links)) # Loại bỏ link trùng nếu có
    except Exception as e:
        print(f"Lỗi khi lấy link từ trang {page}: {e}")
        return []

def get_product_details(url, config=None):
    """Truy cập vào link sản phẩm cụ thể để lấy thông tin chi tiết và đồng nhất đặc trưng."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tập hợp các đặc trưng đích theo schema laptop_features.csv
        target_features = [
            'Hãng sản xuất', 'Hệ điều hành', 'Chất liệu vỏ', 'Công nghệ CPU', 'Loại CPU', 
            'Tốc độ CPU', 'Tốc độ tối đa', 'Loại RAM', 'Dung lượng RAM', 'Tốc độ bus', 
            'Hỗ trợ RAM tối đa', 'Loại ổ cứng', 'Dung lượng ổ cứng', 'Kích thước', 
            'Độ phân giải', 'Công nghệ màn hình', 'Bộ xử lý', 'Kiểu card đồ họa', 
            'Công nghệ âm thanh', 'Cổng giao tiếp', 'Kết nối không dây', 'Webcam', 
            'Đèn bàn phím', 'Loại Pin', 'Dung lượng', 'Kích thước_2', 'Trọng lượng', 
            'source_url', 'shop_1_name', 'shop_1_price', 'shop_1_link', 'shop_2_name', 
            'shop_2_price', 'shop_2_link', 'shop_3_name', 'shop_3_price', 'shop_3_link', 
            'Khe thẻ nhớ', 'Tính năng khác', 'Dung lượng VGA'
        ]
        
        # Khởi tạo row với các giá trị rỗng
        row = {feat: "" for feat in target_features}
        row['shop_1_name'] = "Chợ Tốt"
        
        # 1. Trích xuất giá và làm sạch
        price_tag = soup.find('b', class_='p1mdjmwc')
        if price_tag:
            price_str = price_tag.get_text(strip=True).replace('.', '').replace(' đ', '').replace(',', '')
            row['shop_1_price'] = price_str
            
        # 2. Ánh xạ đặc trưng từ Chợ Tốt sang Schema chung
        mapping = {
            'Hãng': 'Hãng sản xuất',
            'Bộ vi xử lý': 'Công nghệ CPU',
            'RAM': 'Dung lượng RAM',
            'Ổ cứng': 'Dung lượng ổ cứng',
            'Kích cỡ màn hình': 'Kích thước',
            'Card màn hình': 'Bộ xử lý',
            'Loại ổ cứng': 'Loại ổ cứng'
        }
        
        others = []
        spec_items = soup.find_all('div', class_='p74axq8')
        for item in spec_items:
            label_tag = item.find('div', class_='psxqsiz')
            value_tag = item.find('div', class_='p1vpox21')
            
            if label_tag and value_tag:
                label = label_tag.get_text(strip=True).replace(':', '')
                value = value_tag.get_text(strip=True)
                
                if label in mapping:
                    row[mapping[label]] = value
                else:
                    others.append(f"{label}: {value}")
        
        # 3. Gộp các thông tin thừa vào 'Tính năng khác'
        title_tag = soup.find('h1')
        if title_tag:
            others.append(f"Tiêu đề: {title_tag.get_text(strip=True)}")
            
        row['Tính năng khác'] = " | ".join(others)
                    
        return row
    except Exception as e:
        print(f"Lỗi khi lấy chi tiết từ {url}: {e}")
        return None
