def suggest_size(height, weight, gender="unisex"):
    bmi = weight / ((height / 100) ** 2)
    if gender == "female":
        if bmi < 17.5: return "XS"
        elif bmi < 20: return "S"
        elif bmi < 24: return "M"
        elif bmi < 28: return "L"
        elif bmi < 32: return "XL"
        else: return "XXL"
    elif gender == "male":
        if bmi < 18.5: return "S"
        elif bmi < 22: return "M"
        elif bmi < 26: return "L"
        elif bmi < 30: return "XL"
        else: return "XXL"
    else:
        if bmi < 18.5: return "S"
        elif bmi < 23: return "M"
        elif bmi < 27.5: return "L"
        elif bmi < 32: return "XL"
        else: return "XXL"

def get_body_type(height, weight):
    bmi = weight / ((height / 100) ** 2)
    if bmi < 18.5:
        return {"label":"Slim","icon":"🌿","tip":"Fitted silhouettes and structured fabrics add dimension.","color":"#5ECFA0"}
    elif bmi < 25:
        return {"label":"Athletic","icon":"⚡","tip":"Most cuts work great — try slim or tailored fits.","color":"#7C6FE0"}
    elif bmi < 30:
        return {"label":"Curvy","icon":"✨","tip":"A-line and wrap styles beautifully complement your shape.","color":"#E8A598"}
    else:
        return {"label":"Full Figure","icon":"🌸","tip":"Empire waists and draped fabrics offer comfort and style.","color":"#F4C07A"}

def get_fit_tips(size, garment_type="top"):
    tips = {
        "top": {
            "XS": ["Look for stretch fabrics","Cropped tops work well","Layer with oversized pieces"],
            "S":  ["Most fitted styles suit you","Try tucked-in shirts","Puff sleeves add volume"],
            "M":  ["Classic straight-cut tees","Button-downs fit easily","Blazers look sharp"],
            "L":  ["Relaxed fit for comfort","Wrap tops are flattering","V-necks elongate"],
            "XL": ["Flowy fabrics drape well","Structured shoulders balance","Monochrome elevates"],
            "XXL":["Empire cuts flatter","Dark tones are slimming","Wide-leg pairs well"],
        },
        "bottom": {
            "XS": ["High-waist defines shape","Mini skirts work well","Skinny jeans fit easily"],
            "S":  ["Wide-leg trousers look chic","High-waist flatters","Pleated skirts add volume"],
            "M":  ["Straight-cut is versatile","Midi skirts suit all occasions","Chinos are classic"],
            "L":  ["Bootcut balances proportions","A-line skirts are flattering","Relaxed chinos"],
            "XL": ["Flared legs elongate","Elastic waist for comfort","Palazzo pants are chic"],
            "XXL":["Wide-leg trousers slim","Dark bottoms elongate","Stretchy waistbands"],
        }
    }
    return tips.get(garment_type, tips["top"]).get(size, ["Try before you buy for best fit"])

def get_size_chart(gender="unisex"):
    if gender == "female":
        return [
            {"size":"XS","chest":"30–32\"","waist":"22–24\"","hips":"32–34\""},
            {"size":"S", "chest":"32–34\"","waist":"24–26\"","hips":"34–36\""},
            {"size":"M", "chest":"34–36\"","waist":"26–28\"","hips":"36–38\""},
            {"size":"L", "chest":"36–40\"","waist":"28–32\"","hips":"38–42\""},
            {"size":"XL","chest":"40–44\"","waist":"32–36\"","hips":"42–46\""},
            {"size":"XXL","chest":"44–48\"","waist":"36–40\"","hips":"46–50\""},
        ]
    elif gender == "male":
        return [
            {"size":"S",  "chest":"34–36\"","waist":"28–30\"","hips":"34–36\""},
            {"size":"M",  "chest":"38–40\"","waist":"32–34\"","hips":"38–40\""},
            {"size":"L",  "chest":"42–44\"","waist":"36–38\"","hips":"42–44\""},
            {"size":"XL", "chest":"46–48\"","waist":"40–42\"","hips":"46–48\""},
            {"size":"XXL","chest":"50–52\"","waist":"44–46\"","hips":"50–52\""},
        ]
    else:
        return [
            {"size":"S",  "chest":"32–36\"","waist":"26–30\"","hips":"34–38\""},
            {"size":"M",  "chest":"36–40\"","waist":"30–34\"","hips":"38–42\""},
            {"size":"L",  "chest":"40–44\"","waist":"34–38\"","hips":"42–46\""},
            {"size":"XL", "chest":"44–48\"","waist":"38–42\"","hips":"46–50\""},
            {"size":"XXL","chest":"48–52\"","waist":"42–46\"","hips":"50–54\""},
        ]