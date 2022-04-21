import re


def pretexts_get():
    return (
        # English
        'the', 'in', 'do', 'non', 'there', 'are', 'at', 'they', 'their', 'on', 'this', 'that', 'under', 'above',
        'between', 'to', 'into', 'out',
        'of', 'from', 'through', 'along', 'across', 'by', 'before', 'after', 'till', 'until', 'ago', 'is', 'during',
        'since', 'for',
        'because', 'with', 'and', 'wer', 'was', 'including', 'against', 'among', 'throughout', 'despite', 'towards',
        'upon',
        'concerning', 'to', 'by', 'about', 'like', 'over', 'before', 'since', 'without', 'within', 'along', 'following',
        'across', 'behind', 'beyond',
        'plus', 'except', 'but', 'up', 'around', 'down', 'off', 'above', 'near',
        # german
        'bis', 'durch', 'ohne', 'gegen', 'um', 'entlang', 'ab', 'aus', 'für', 'bei', 'Mit', 'Nach', 'Seit', 'Von', 'Zu',
        'An', 'Auf', 'Hinter',
        'Neben', 'außer', 'dank', 'entgegen', 'gegenüber', 'gemäß', 'laut', 'seit', 'zufolge', 'über', 'unter',
        'zwischen', 'anstatt', 'außerhalb',
        'beiderseits', 'diesseits', 'innerhalb', 'jenseits', 'oberhalb', 'trotz', 'unterhalb', 'wegen', 'während',
        # russian
        'без', 'близ', 'в', 'во', 'вместо', 'не', 'вне', 'для', 'до', 'за', 'из', 'из-за', 'из-под', 'к', 'ко', 'кроме',
        'между', 'на', 'над', 'о',
        'от', 'перед', 'по', 'под', 'при', 'про', 'ради', 'c', 'среди', 'сквозь', 'у', 'через',
        # portuguese
        'a', 'para', 'acima de', 'antes de', 'perante', 'após', 'depois de', 'até', 'com', 'como', 'de', 'despe',
        'diante', 'perante', 'em', 'sobre',
        'entre', 'para', 'por', 'perto de', 'sob',
        # italian
        'del', 'dello', 'dell', 'della', 'dei', 'degli', 'delle', 'di', 'al', 'allo', 'all', 'alla', 'ai', 'agli',
        'alle', 'a', 'da', 'dal', 'dallo',
        'dall', 'dai', 'dagli', 'dalle', 'nel', 'nello', 'nell', 'nella', 'nei', 'negli', 'nelle', 'su', 'sul', 'sullo',
        'sull', 'sulla', 'sui',
        'sugli', 'sulle',
        # vietnamese
        'về', 'trên đây', 'ngang qua', 'sau khi', 'chống lại', 'trong số', 'xung quanh', 'như', 'tại', 'trước khi',
        'sau', 'dưới đây', 'bên dưới',
        'bên cạnh', 'giữa', 'ngoài', 'nhưng', 'bởi', 'mặc dù', 'xuống', 'trong khi', 'ngoại trừ', 'cho', 'từ', 'trong',
        'bên trong', 'vào trong', 'gần',
        'tiếp theo', 'của', 'trên', 'đối diện', 'ra', 'bên ngoài', 'trên', 'mỗi', 'Dưới', 'thêm', 'tròn', '	kể từ',
        'hơn', 'thông qua', 'đến', 'về phía',
        'không giống như', 'cho đến khi', 'lên', 'thông qua', 'với', 'trong vòng', 'mà không cần', 'cái này', 'cái đó',
        'những cái này', 'những cái đó',
        # uzbek
        'haqida', 'tepada', 'orqali', 'ichidan', 'keyin', 'qarshi', 'o\'rtasida', 'atrofida', 'taxminan', 'o\'xshab',
        'o\'stida', 'ichida', 'oldin',
        'orqada', 'pastda', 'ostida', 'yonma-yon', 'o\'rtasida', 'orqasida', 'narigi tomonida', 'lekin', 'yonida',
        'tomonidan', 'ga qaramay',
        'past tomoniga', 'davomida', 'mobaynida', 'dan tashqari', 'uchun', 'ichida', 'ichiga', 'yonida', 'atrofida',
        'qarama-qarshi', '	tashqarida',
        'tepasida', 'qo\'shuv', 'taxminan', 'beri', 'ko\'ra', 'orasidan', 'gacha', 'tagida', 'pastida', 'o\'xshamasdan',
        'bilan', 'bu', 'u', 'bular',
        'ular',
        # azerbaijani
        'haqqında', 'yuxarıda', 'o tərəfə', 'sonra', 'qarşı', 'arasında', 'ətrafında', 'kimi', 'yanında', 'əvvəl',
        'arxasında', 'aşağıda', 'altında',
        'yanaşı', 'arasında', 'kənarda', 'lakin', 'ilə', 'baxmayaraq', 'aşağı', 'ərzində', 'istisna olmaqla', 'üçün',
        'içərisində', 'içəriyə', 'yaxın',
        'sonrakı', 'üstündə', 'qarşısında', 'bayıra', 'kənarda', 'üstündə', 'hər', 'üstəgəl', 'dairəvi', 'etibarən',
        'nisbətən', 'vasitəsilə', 'qədər',
        'doğru', 'doğru', 'altında', 'fərqli', 'qədər', 'yuxarı', 'vasitəsilə', 'ərzində', 'olmadan',
        # thai
        'เกี่ยวกับ', 'เหนือ', 'ข้าม', 'หลังจาก', 'ต่อ', 'ระหว่าง', 'รอบ', 'เช่น', 'ที่', 'ก่อน', 'ข้างหลัง', 'ข้างล่าง',
        'ภายใต้', 'ข้างๆ', 'ระหว่าง', 'เกิน', 'แต่', 'โดย',
        'แม้จะ มี', 'ลง', 'ในระหว่าง', 'ยกเว้น', 'สำหรับ', 'จาก', 'ใน', 'ข้างใน', 'เข้าไป', 'ใกล้', 'ถัดไป', 'ของ',
        'เกี่ยวกับ', 'ตรงข้าม', 'ออก', 'ข้างนอก', '	เกิน',
        'ต่อ', 'บวก', 'รอบ', 'ตั้งแต่', 'กว่า', 'ผ่าน', 'จนถึง', 'ไปยัง', 'สู่', 'ภายใต้', 'ไม่เหมือนกัน', 'จนกระทั่ง',
        'ขึ้นไป', 'ผ่าน ทาง', 'ด้วย - dûay', 'ภายใน',
        'ไม่มี , ไม่เกี่ยว', 'นี้', 'นั้น', 'เหล่านี้', 'เหล่านั้น'
        # indonesian
                                                        'atas', 'Atas', 'Setelah', 'Sekitar', 'Karena', 'Sebelum',
        'Samping', 'Antara', 'Tapi', 'Dekat ke', 'Turun', 'Selama', 'Untuk', 'Dari', 'depan',
        'Dalam', 'Daripada', 'Seperti', 'Dekat', 'Berdekatan', 'puncak', 'Keluar', 'Luar', 'Diatas', 'seberang',
        'Tentang', 'sejak', 'Daripada', 'ke',
        'bawah', 'Sampai', 'Naik', 'Tanpa', 'Tentang'
    )


def compare_pretext(result_text, *args):
    for pretext in pretexts_get():
        regular_pretext = re.findall(pretext, args[0], re.M | re.I)
        try:
            for regular in range(len(regular_pretext)):
                args[1].remove(pretext)
        except ValueError:
            continue
    return counting_elements(result_text, args[1], args[2])


def counting_elements(result_text, *args):
    for text in args[0]:
        regular_text = re.findall(text, args[1], re.I)
        set_element = (text, len(regular_text))
        result_text.add(set_element)
    return None


def export_dict(result_text):
    export = dict()

    for text in result_text:
        if text[0] not in export:
            export[text[0]] = 0

        export[text[0]] += text[1]

    return export


def tags_extract(text):
    result_text = set()
    change_text = re.sub(r'[^\w\s]', '', text)
    list_text = change_text.lower().split()
    compare_pretext(result_text, change_text, list_text, text)
    return export_dict(result_text)


def tags_extract_v2(text):
    arr = []
    block_words = pretexts_get()
    for word in text.split(' '):
        if word not in block_words:
            arr.append(word)
    return arr
