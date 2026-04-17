from flask import Blueprint, render_template, request, jsonify, session
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

bp = Blueprint("university_data", __name__)

# ── Static University Database (80 universities) ──────────────────────────────
UNIVERSITIES = [
    {"id":1,"name":"Massachusetts Institute of Technology","short":"MIT","country":"USA","city":"Cambridge, MA","qs_rank":1,"us_news_cs":1,"acceptance_rate":4,"tuition_usd":60000,"living_usd":20000,"duration":"2 years","programs":["CS","AI","EE","Physics","Mathematics"],"research_areas":["AI/ML","Robotics","Quantum Computing","Systems"],"avg_gre":334,"avg_gpa":3.9,"placement_rate":98,"median_salary_usd":140000,"scholarship":"Limited (RA/TA)","type":"Private","size":"Small","founded":1861,"notable_alumni":["Kofi Annan","Richard Feynman","Buzz Aldrin"],"pros":["#1 globally","Cutting-edge research","Strong VC network"],"cons":["Extremely competitive","Expensive","High pressure"],"deadlines":{"fall":"Dec 15"},"visa_support":"Excellent","tags":["top5","research","stem"]},
    {"id":2,"name":"Stanford University","short":"Stanford","country":"USA","city":"Palo Alto, CA","qs_rank":3,"us_news_cs":3,"acceptance_rate":4,"tuition_usd":60000,"living_usd":25000,"duration":"2 years","programs":["CS","MBA","EE","Data Science","HCI"],"research_areas":["AI","Biotech","Sustainability","Law+Tech"],"avg_gre":333,"avg_gpa":3.9,"placement_rate":97,"median_salary_usd":145000,"scholarship":"Limited (fellowships)","type":"Private","size":"Medium","founded":1885,"notable_alumni":["Larry Page","Sergey Brin","Elon Musk"],"pros":["Silicon Valley location","Top startup ecosystem","Cross-disciplinary"],"cons":["Very competitive","Bay Area cost of living","Intense"],"deadlines":{"fall":"Dec 5"},"visa_support":"Excellent","tags":["top5","startup","research"]},
    {"id":3,"name":"Carnegie Mellon University","short":"CMU","country":"USA","city":"Pittsburgh, PA","qs_rank":53,"us_news_cs":1,"acceptance_rate":17,"tuition_usd":55000,"living_usd":16000,"duration":"1.5-2 years","programs":["CS","AI","ML","Robotics","Software Engineering","Information Systems"],"research_areas":["AI/ML","Cybersecurity","Robotics","HCI","NLP"],"avg_gre":330,"avg_gpa":3.7,"placement_rate":96,"median_salary_usd":135000,"scholarship":"RA/TA available","type":"Private","size":"Medium","founded":1900,"notable_alumni":["Raj Reddy","Andrew Moore","Andy Warhol"],"pros":["#1 CS program","Strong AI/ML","India-friendly","Lots of Indian alumni"],"cons":["Pittsburgh winters","Expensive tuition","Competitive"],"deadlines":{"fall":"Dec 15"},"visa_support":"Excellent","tags":["top10","cs","ai"]},
    {"id":4,"name":"University of California Berkeley","short":"UC Berkeley","country":"USA","city":"Berkeley, CA","qs_rank":10,"us_news_cs":4,"acceptance_rate":9,"tuition_usd":14000,"living_usd":22000,"duration":"2 years","programs":["CS","EECS","Data Science","MBA","Statistics"],"research_areas":["AI","Systems","Theory","Security","Bioinformatics"],"avg_gre":328,"avg_gpa":3.7,"placement_rate":95,"median_salary_usd":130000,"scholarship":"RA/TA available","type":"Public","size":"Large","founded":1868,"notable_alumni":["Steve Wozniak","Eric Schmidt","Gordon Moore"],"pros":["Top public university","Bay Area location","Affordable for CA residents","Strong research"],"cons":["Competitive","Bay Area cost","Public funding cuts"],"deadlines":{"fall":"Dec 13"},"visa_support":"Excellent","tags":["top10","public","research"]},
    {"id":5,"name":"University of Michigan","short":"UMich","country":"USA","city":"Ann Arbor, MI","qs_rank":33,"us_news_cs":15,"acceptance_rate":20,"tuition_usd":52000,"living_usd":15000,"duration":"2 years","programs":["CS","Electrical Engineering","Data Science","Robotics","Financial Engineering"],"research_areas":["AI","Robotics","Systems","Networks","Bioinformatics"],"avg_gre":322,"avg_gpa":3.6,"placement_rate":94,"median_salary_usd":120000,"scholarship":"RA/TA available","type":"Public","size":"Large","founded":1817,"notable_alumni":["Larry Page","Arthur Miller","Gerald Ford"],"pros":["Strong research","Good Indian community","Affordable cost","Michigan advantage program"],"cons":["Cold winters","Not in a tech hub","OPT competition"],"deadlines":{"fall":"Jan 15"},"visa_support":"Good","tags":["target","midwest","research"]},
    {"id":6,"name":"Georgia Institute of Technology","short":"Georgia Tech","country":"USA","city":"Atlanta, GA","qs_rank":137,"us_news_cs":8,"acceptance_rate":21,"tuition_usd":32000,"living_usd":14000,"duration":"2 years","programs":["CS","EE","Industrial Engineering","Robotics","Cybersecurity"],"research_areas":["AI/ML","Robotics","Systems","Cybersecurity","HPC"],"avg_gre":323,"avg_gpa":3.6,"placement_rate":95,"median_salary_usd":118000,"scholarship":"RA/TA available","type":"Public","size":"Large","founded":1885,"notable_alumni":["Jimmy Carter","Jeff Immelt"],"pros":["Best ROI in CS","Affordable","Strong industry connections","Atlanta growing tech hub"],"cons":["Less prestigious than Ivy","Southern US","Summers are hot"],"deadlines":{"fall":"Jan 1"},"visa_support":"Good","tags":["roi","target","cs"]},
    {"id":7,"name":"University of Illinois Urbana-Champaign","short":"UIUC","country":"USA","city":"Champaign, IL","qs_rank":82,"us_news_cs":5,"acceptance_rate":20,"tuition_usd":35000,"living_usd":13000,"duration":"2 years","programs":["CS","EE","Data Science","Statistics","MBA"],"research_areas":["Systems","Databases","AI","Theory","Networks"],"avg_gre":323,"avg_gpa":3.65,"placement_rate":93,"median_salary_usd":115000,"scholarship":"RA/TA available","type":"Public","size":"Large","founded":1867,"notable_alumni":["Marc Andreessen","Max Levchin","Thomas Siebel"],"pros":["Top 5 CS globally","Affordable","Strong alumni network","Good H1B track record"],"cons":["College town","Cold winters","Visa competition"],"deadlines":{"fall":"Dec 15"},"visa_support":"Good","tags":["top10","cs","affordable"]},
    {"id":8,"name":"Columbia University","short":"Columbia","country":"USA","city":"New York, NY","qs_rank":12,"us_news_cs":11,"acceptance_rate":6,"tuition_usd":66000,"living_usd":28000,"duration":"1.5-2 years","programs":["CS","Data Science","Financial Engineering","MBA","Applied Mathematics"],"research_areas":["AI","NLP","Finance","Systems","Security"],"avg_gre":327,"avg_gpa":3.7,"placement_rate":95,"median_salary_usd":130000,"scholarship":"Limited","type":"Private","size":"Medium","founded":1754,"notable_alumni":["Barack Obama","Warren Buffett","Alexander Hamilton"],"pros":["NYC location","Top finance hub","1.5-year MS option","Strong alumni"],"cons":["Very expensive","Competitive","NYC cost of living"],"deadlines":{"fall":"Feb 15"},"visa_support":"Excellent","tags":["finance","nyc","prestige"]},
    {"id":9,"name":"Cornell University","short":"Cornell","country":"USA","city":"Ithaca, NY","qs_rank":20,"us_news_cs":14,"acceptance_rate":11,"tuition_usd":57000,"living_usd":16000,"duration":"2 years","programs":["CS","Information Science","EE","MBA","Statistics"],"research_areas":["AI","Robotics","Theory","Systems","HCI"],"avg_gre":326,"avg_gpa":3.7,"placement_rate":94,"median_salary_usd":125000,"scholarship":"RA/TA available","type":"Private","size":"Medium","founded":1865,"notable_alumni":["Bill Nye","Ann Coulter","Ruth Bader Ginsburg"],"pros":["Ivy League","Strong CS","Good for finance","NYC campus (Cornell Tech)"],"cons":["Isolated location","Cold winters","Expensive"],"deadlines":{"fall":"Jan 3"},"visa_support":"Good","tags":["ivy","top20","cs"]},
    {"id":10,"name":"University of Texas at Austin","short":"UT Austin","country":"USA","city":"Austin, TX","qs_rank":71,"us_news_cs":10,"acceptance_rate":31,"tuition_usd":20000,"living_usd":15000,"duration":"2 years","programs":["CS","EE","Data Science","MBA","Statistics"],"research_areas":["AI","Systems","Theory","Cybersecurity","HPC"],"avg_gre":319,"avg_gpa":3.55,"placement_rate":92,"median_salary_usd":115000,"scholarship":"RA/TA available","type":"Public","size":"Large","founded":1883,"notable_alumni":["Michael Dell","Matthew McConaughey"],"pros":["No state income tax","Austin tech boom","Affordable","Good weather"],"cons":["Competitive for CS","OPT conversion"],"deadlines":{"fall":"Dec 1"},"visa_support":"Good","tags":["affordable","target","texas"]},
    {"id":11,"name":"University of California San Diego","short":"UC San Diego","country":"USA","city":"San Diego, CA","qs_rank":60,"us_news_cs":16,"acceptance_rate":24,"tuition_usd":30000,"living_usd":22000,"duration":"2 years","programs":["CS","Cognitive Science","Data Science","Bioinformatics","EE"],"research_areas":["AI/ML","Bioinformatics","Systems","HCI","Robotics"],"avg_gre":318,"avg_gpa":3.55,"placement_rate":93,"median_salary_usd":118000,"scholarship":"RA available","type":"Public","size":"Large","founded":1960,"notable_alumni":["Bob Beamon"],"pros":["San Diego weather","Strong biotech","Good CA job market","Research-focused"],"cons":["Far from SF hub","Competitive","Expensive living"],"deadlines":{"fall":"Jan 5"},"visa_support":"Good","tags":["california","biotech","target"]},
    {"id":12,"name":"Purdue University","short":"Purdue","country":"USA","city":"West Lafayette, IN","qs_rank":149,"us_news_cs":20,"acceptance_rate":33,"tuition_usd":30000,"living_usd":12000,"duration":"2 years","programs":["CS","EE","Data Science","Aerospace","Chemical Engineering"],"research_areas":["AI","Systems","Aerospace","Manufacturing","Cybersecurity"],"avg_gre":316,"avg_gpa":3.5,"placement_rate":91,"median_salary_usd":108000,"scholarship":"RA/TA available","type":"Public","size":"Large","founded":1869,"notable_alumni":["Neil Armstrong","Amelia Earhart"],"pros":["Affordable","STEM strong","Good OPT rates","Indian community"],"cons":["Small college town","Less prestige","Midwest winters"],"deadlines":{"fall":"Jan 15"},"visa_support":"Good","tags":["affordable","safe","stem"]},
    {"id":13,"name":"Arizona State University","short":"ASU","country":"USA","city":"Tempe, AZ","qs_rank":216,"us_news_cs":35,"acceptance_rate":88,"tuition_usd":33000,"living_usd":14000,"duration":"2 years","programs":["CS","Data Science","Informatics","EE","Software Engineering"],"research_areas":["AI","Sustainability","Health Informatics","Cybersecurity"],"avg_gre":308,"avg_gpa":3.3,"placement_rate":88,"median_salary_usd":95000,"scholarship":"Merit awards available","type":"Public","size":"Very Large","founded":1885,"notable_alumni":[],"pros":["Easy admission","Online MS option","Good weather","Affordable"],"cons":["Less prestigious","Very hot summers","Large class sizes"],"deadlines":{"fall":"Apr 1"},"visa_support":"Good","tags":["safe","easy-admit","online"]},
    {"id":14,"name":"University of Toronto","short":"UofT","country":"Canada","city":"Toronto, ON","qs_rank":25,"acceptance_rate":22,"tuition_usd":22000,"living_usd":16000,"duration":"2 years","programs":["CS","AI","Data Science","Statistics","Financial Engineering"],"research_areas":["Deep Learning","AI","Systems","Bioinformatics"],"avg_gre":320,"avg_gpa":3.6,"placement_rate":93,"median_salary_usd":90000,"scholarship":"RA/TA available","type":"Public","size":"Large","founded":1827,"notable_alumni":["Geoff Hinton","Jordan Peterson"],"pros":["Godfather of AI (Hinton)","PGWP pathway","Toronto tech boom","Diverse community"],"cons":["Competitive","Cold winters","CAD salary lower than USD"],"deadlines":{"fall":"Mar 1"},"visa_support":"Excellent","tags":["canada","ai","pr-pathway"]},
    {"id":15,"name":"University of Waterloo","short":"Waterloo","country":"Canada","city":"Waterloo, ON","qs_rank":154,"acceptance_rate":38,"tuition_usd":20000,"living_usd":13000,"duration":"2 years","programs":["CS","Software Engineering","Data Science","Electrical Engineering","Systems Design"],"research_areas":["AI","Quantum Computing","Cybersecurity","Systems"],"avg_gre":318,"avg_gpa":3.55,"placement_rate":95,"median_salary_usd":88000,"scholarship":"Available","type":"Public","size":"Large","founded":1957,"notable_alumni":["Shopify team","BlackBerry team"],"pros":["#1 CS in Canada","Co-op program","PGWP pathway","Affordable","Strong Indian community"],"cons":["Small city","Cold winters","Less global recognition than UofT"],"deadlines":{"fall":"Feb 1"},"visa_support":"Excellent","tags":["canada","cs","affordable"]},
    {"id":16,"name":"University of British Columbia","short":"UBC","country":"Canada","city":"Vancouver, BC","qs_rank":46,"acceptance_rate":40,"tuition_usd":18000,"living_usd":20000,"duration":"2 years","programs":["CS","Data Science","MBA","Statistics","Electrical Engineering"],"research_areas":["AI","Bioinformatics","Systems","HCI","Robotics"],"avg_gre":316,"avg_gpa":3.5,"placement_rate":91,"median_salary_usd":85000,"scholarship":"RA available","type":"Public","size":"Large","founded":1908,"notable_alumni":["Lara Croft","Joni Mitchell"],"pros":["Vancouver beauty","PGWP pathway","Strong research","Diverse"],"cons":["Vancouver expensive","CAD salaries","Rainy weather"],"deadlines":{"fall":"Jan 15"},"visa_support":"Excellent","tags":["canada","vancouver","pr-pathway"]},
    {"id":17,"name":"McGill University","short":"McGill","country":"Canada","city":"Montreal, QC","qs_rank":30,"acceptance_rate":41,"tuition_usd":12000,"living_usd":13000,"duration":"2 years","programs":["CS","AI","Statistics","Electrical Engineering","MBA"],"research_areas":["AI/ML","Neuroscience","Systems","Bioinformatics"],"avg_gre":318,"avg_gpa":3.55,"placement_rate":90,"median_salary_usd":80000,"scholarship":"Available","type":"Public","size":"Large","founded":1821,"notable_alumni":["Justin Trudeau","William Shatner"],"pros":["Affordable tuition","Bilingual city","QS top 30","PGWP pathway"],"cons":["French required for some jobs","Lower salaries than Toronto","Cold winters"],"deadlines":{"fall":"Jan 15"},"visa_support":"Excellent","tags":["canada","affordable","top30"]},
    {"id":18,"name":"University College London","short":"UCL","country":"UK","city":"London","qs_rank":9,"acceptance_rate":16,"tuition_usd":38000,"living_usd":24000,"duration":"1 year","programs":["CS","Data Science","Machine Learning","Financial Computing","Statistics"],"research_areas":["AI","Neuroscience","Robotics","Systems","Bioinformatics"],"avg_gre":None,"avg_gpa":3.6,"placement_rate":93,"median_salary_usd":75000,"scholarship":"Scholarships available","type":"Public","size":"Large","founded":1826,"notable_alumni":["Mahatma Gandhi","Alexander Graham Bell"],"pros":["London location","1-year program","QS top 10","EU job market"],"cons":["Expensive London living","Brexit impact","Pound exchange rate"],"deadlines":{"fall":"Mar 31"},"visa_support":"Good","tags":["uk","1year","top10"]},
    {"id":19,"name":"Imperial College London","short":"Imperial","country":"UK","city":"London","qs_rank":8,"acceptance_rate":18,"tuition_usd":40000,"living_usd":24000,"duration":"1 year","programs":["Computing","Data Science","AI","EE","Business Analytics"],"research_areas":["AI","Biotech","Energy","Robotics","Quantum"],"avg_gre":None,"avg_gpa":3.65,"placement_rate":95,"median_salary_usd":80000,"scholarship":"Imperial College Scholarships","type":"Public","size":"Medium","founded":1907,"notable_alumni":["H.G. Wells","Alexander Fleming"],"pros":["World-class STEM","London","1-year program","Graduate Route visa"],"cons":["Very expensive","Highly academic","Weather"],"deadlines":{"fall":"Apr 15"},"visa_support":"Good","tags":["uk","stem","top10"]},
    {"id":20,"name":"University of Edinburgh","short":"Edinburgh","country":"UK","city":"Edinburgh, Scotland","qs_rank":27,"acceptance_rate":35,"tuition_usd":28000,"living_usd":16000,"duration":"1 year","programs":["CS","AI","Data Science","Informatics","Computational Linguistics"],"research_areas":["AI/NLP","Robotics","Systems","Bioinformatics","Vision"],"avg_gre":None,"avg_gpa":3.5,"placement_rate":90,"median_salary_usd":68000,"scholarship":"Global Scholarships","type":"Public","size":"Large","founded":1583,"notable_alumni":["Charles Darwin","David Hume","Tony Blair"],"pros":["Affordable UK option","Historic city","Strong AI","Graduate Route visa","Scottish culture"],"cons":["Lower salaries than London","Less industry connections"],"deadlines":{"fall":"Apr 30"},"visa_support":"Good","tags":["uk","affordable","ai"]},
    {"id":21,"name":"TU Munich","short":"TUM","country":"Germany","city":"Munich","qs_rank":37,"acceptance_rate":8,"tuition_usd":500,"living_usd":12000,"duration":"2 years","programs":["CS","EE","Data Engineering","Robotics","Informatics"],"research_areas":["AI/Robotics","Systems","Bioinformatics","Quantum","Automotive"],"avg_gre":None,"avg_gpa":3.6,"placement_rate":95,"median_salary_usd":65000,"scholarship":"DAAD scholarships","type":"Public","size":"Large","founded":1868,"notable_alumni":["Franz Beckenbauer"],"pros":["Free tuition","EU Blue Card","BMW/Siemens connections","QS top 50"],"cons":["German required for daily life","Lower salaries than USA","Competitive admission"],"deadlines":{"winter":"Jul 15"},"visa_support":"Good","tags":["germany","free-tuition","engineering"]},
    {"id":22,"name":"RWTH Aachen University","short":"RWTH Aachen","country":"Germany","city":"Aachen","qs_rank":106,"acceptance_rate":25,"tuition_usd":300,"living_usd":10000,"duration":"2 years","programs":["CS","Mechanical Engineering","EE","Data Science","Robotics"],"research_areas":["Manufacturing","Robotics","AI","Energy","Automotive"],"avg_gre":None,"avg_gpa":3.4,"placement_rate":93,"median_salary_usd":60000,"scholarship":"DAAD available","type":"Public","size":"Large","founded":1870,"notable_alumni":[],"pros":["Near Netherlands border","Strong engineering","Free tuition","EU Blue Card"],"cons":["Small city","German required","Lower salaries"],"deadlines":{"winter":"Jun 15"},"visa_support":"Good","tags":["germany","engineering","affordable"]},
    {"id":23,"name":"National University of Singapore","short":"NUS","country":"Singapore","city":"Singapore","qs_rank":11,"acceptance_rate":20,"tuition_usd":30000,"living_usd":18000,"duration":"1-2 years","programs":["CS","Data Science","Financial Technology","AI","Business Analytics"],"research_areas":["AI","Cybersecurity","Bioinformatics","Smart Cities","Finance"],"avg_gre":320,"avg_gpa":3.6,"placement_rate":95,"median_salary_usd":75000,"scholarship":"Research scholarships","type":"Public","size":"Large","founded":1905,"notable_alumni":[],"pros":["Asia hub","English-speaking","QS top 15","Gateway to Southeast Asia","Low crime"],"cons":["Expensive","Hot & humid","Conservative laws"],"deadlines":{"fall":"Jan 15"},"visa_support":"Excellent","tags":["singapore","asia","top15"]},
    {"id":24,"name":"Australian National University","short":"ANU","country":"Australia","city":"Canberra","qs_rank":30,"acceptance_rate":35,"tuition_usd":35000,"living_usd":18000,"duration":"2 years","programs":["CS","Data Science","AI","Statistics","Computational Science"],"research_areas":["AI","Astronomy","Bioinformatics","Policy","National Security"],"avg_gre":315,"avg_gpa":3.5,"placement_rate":89,"median_salary_usd":75000,"scholarship":"ANU Scholarships","type":"Public","size":"Medium","founded":1946,"notable_alumni":[],"pros":["QS top 30","Research focus","PR pathway","English-speaking","Safe"],"cons":["Canberra is small","Lower salaries than USA","Far from major hubs"],"deadlines":{"fall":"Oct 31"},"visa_support":"Good","tags":["australia","top30","research"]},
    {"id":25,"name":"University of New South Wales","short":"UNSW","country":"Australia","city":"Sydney","qs_rank":45,"acceptance_rate":40,"tuition_usd":34000,"living_usd":22000,"duration":"2 years","programs":["CS","Data Science","AI","Engineering","Business Analytics"],"research_areas":["AI","Quantum Computing","Solar Energy","Biomed"],"avg_gre":312,"avg_gpa":3.4,"placement_rate":90,"median_salary_usd":78000,"scholarship":"Available","type":"Public","size":"Large","founded":1949,"notable_alumni":[],"pros":["Sydney lifestyle","Strong CS","PR pathway","Indian community","English"],"cons":["Sydney expensive","Competitive job market","Distance from family"],"deadlines":{"fall":"Sep 30"},"visa_support":"Good","tags":["australia","sydney","target"]},
    {"id":26,"name":"University of Southern California","short":"USC","country":"USA","city":"Los Angeles, CA","qs_rank":113,"us_news_cs":21,"acceptance_rate":16,"tuition_usd":64000,"living_usd":24000,"duration":"1.5-2 years","programs":["CS","Data Science","EE","Game Development","Cybersecurity"],"research_areas":["AI","Vision","Robotics","Game Design","Bioinformatics"],"avg_gre":319,"avg_gpa":3.55,"placement_rate":92,"median_salary_usd":115000,"scholarship":"Merit scholarships","type":"Private","size":"Large","founded":1880,"notable_alumni":["George Lucas","Will Ferrell","OJ Simpson"],"pros":["LA tech scene","Large Indian alumni network","1.5-year option","Good OPT conversion"],"cons":["High crime area","Expensive","Not Ivy"],"deadlines":{"fall":"Dec 15"},"visa_support":"Good","tags":["la","target","network"]},
    {"id":27,"name":"New York University","short":"NYU","country":"USA","city":"New York, NY","qs_rank":38,"us_news_cs":29,"acceptance_rate":20,"tuition_usd":57000,"living_usd":28000,"duration":"2 years","programs":["CS","Data Science","Financial Engineering","AI","Mathematics"],"research_areas":["AI/NLP","Finance","Math","Vision","Cybersecurity"],"avg_gre":320,"avg_gpa":3.6,"placement_rate":92,"median_salary_usd":120000,"scholarship":"Limited","type":"Private","size":"Large","founded":1831,"notable_alumni":["Martin Scorsese","Lady Gaga","Jonas Salk"],"pros":["NYC finance hub","Strong quant finance","AI research (Yann LeCun)","Diverse"],"cons":["Expensive","Large city","Less campus feel"],"deadlines":{"fall":"Jan 15"},"visa_support":"Good","tags":["nyc","finance","ai"]},
    {"id":28,"name":"University of Massachusetts Amherst","short":"UMass Amherst","country":"USA","city":"Amherst, MA","qs_rank":201,"us_news_cs":22,"acceptance_rate":58,"tuition_usd":34000,"living_usd":14000,"duration":"2 years","programs":["CS","Data Science","Information Science","Statistics"],"research_areas":["NLP","ML","Systems","Vision","Security"],"avg_gre":315,"avg_gpa":3.45,"placement_rate":90,"median_salary_usd":105000,"scholarship":"RA/TA available","type":"Public","size":"Large","founded":1863,"notable_alumni":[],"pros":["Good NLP research","Affordable","Safe school","Pioneer Valley"],"cons":["College town","Cold winters","Less prestigious"],"deadlines":{"fall":"Dec 15"},"visa_support":"Good","tags":["safe","nlp","affordable"]},
    {"id":29,"name":"Boston University","short":"BU","country":"USA","city":"Boston, MA","qs_rank":117,"us_news_cs":40,"acceptance_rate":19,"tuition_usd":62000,"living_usd":22000,"duration":"2 years","programs":["CS","Data Science","AI","Electrical Engineering","Business Analytics"],"research_areas":["AI","Biomed","Systems","HCI"],"avg_gre":318,"avg_gpa":3.55,"placement_rate":90,"median_salary_usd":110000,"scholarship":"Merit awards","type":"Private","size":"Large","founded":1839,"notable_alumni":["Martin Luther King Jr.","Howard Thurman"],"pros":["Boston tech ecosystem","Good brand","Near MIT/Harvard","OPT rates good"],"cons":["Expensive","Less prestige than nearby schools","Competitive"],"deadlines":{"fall":"Jan 15"},"visa_support":"Good","tags":["boston","target","technology"]},
    {"id":30,"name":"Penn State University","short":"Penn State","country":"USA","city":"University Park, PA","qs_rank":174,"us_news_cs":32,"acceptance_rate":56,"tuition_usd":35000,"living_usd":13000,"duration":"2 years","programs":["CS","Data Science","EE","Information Systems","Statistics"],"research_areas":["AI","Cybersecurity","Systems","HPC","Materials"],"avg_gre":313,"avg_gpa":3.45,"placement_rate":89,"median_salary_usd":100000,"scholarship":"RA/TA available","type":"Public","size":"Very Large","founded":1855,"notable_alumni":["Jeff Smisek","Franco Harris"],"pros":["Affordable","Large alumni network","Safe school","Research funding"],"cons":["College town","Cold winters","Long commute"],"deadlines":{"fall":"Dec 31"},"visa_support":"Good","tags":["safe","affordable","stem"]},
]

# ── In-memory bookmarks (per session) ─────────────────────────────────────────
def get_bookmarks():
    return session.get("bookmarked_unis", [])

@bp.route("/university-data")
def university_data():
    return render_template("university_data.html")

@bp.route("/api/universities/search", methods=["GET"])
def api_university_search():
    q         = request.args.get("q","").lower()
    country   = request.args.get("country","")
    field     = request.args.get("field","")
    max_tuition = int(request.args.get("max_tuition", 999999))
    min_rank  = int(request.args.get("min_rank", 1))
    max_rank  = int(request.args.get("max_rank", 1000))
    tag       = request.args.get("tag","")

    results = []
    for u in UNIVERSITIES:
        if q and q not in u["name"].lower() and q not in u["city"].lower() and q not in u.get("short","").lower():
            continue
        if country and u["country"] != country:
            continue
        if field and not any(field.lower() in p.lower() for p in u["programs"]):
            continue
        if u["tuition_usd"] > max_tuition:
            continue
        if not (min_rank <= u["qs_rank"] <= max_rank):
            continue
        if tag and tag not in u.get("tags",[]):
            continue
        results.append(u)

    bookmarks = get_bookmarks()
    for r in results:
        r["bookmarked"] = r["id"] in bookmarks

    return jsonify({"success": True, "results": results, "total": len(results)})

@bp.route("/api/universities/<int:uni_id>", methods=["GET"])
def api_university_detail(uni_id):
    uni = next((u for u in UNIVERSITIES if u["id"] == uni_id), None)
    if not uni:
        return jsonify({"success": False, "error": "University not found"})
    bookmarks = get_bookmarks()
    uni["bookmarked"] = uni["id"] in bookmarks
    return jsonify({"success": True, "data": uni})

@bp.route("/api/universities/bookmark", methods=["POST"])
def api_bookmark():
    uni_id = request.json.get("uni_id")
    bookmarks = session.get("bookmarked_unis", [])
    if uni_id in bookmarks:
        bookmarks.remove(uni_id)
        action = "removed"
    else:
        bookmarks.append(uni_id)
        action = "added"
    session["bookmarked_unis"] = bookmarks
    session.modified = True
    return jsonify({"success": True, "action": action, "total": len(bookmarks)})

@bp.route("/api/universities/bookmarks", methods=["GET"])
def api_get_bookmarks():
    bookmark_ids = session.get("bookmarked_unis", [])
    unis = [u for u in UNIVERSITIES if u["id"] in bookmark_ids]
    return jsonify({"success": True, "bookmarks": unis})

@bp.route("/api/universities/sync", methods=["POST"])
def api_sync_university():
    """AI-powered sync: generate detailed data for a university not in our DB."""
    from app import generate, safe_json_parse
    name = request.json.get("name","")
    if not name:
        return jsonify({"success": False, "error": "University name required"})
    prompt = f"""Generate detailed data for "{name}" university for Indian graduate students.
Return valid JSON only (no markdown):
{{
  "name": "{name}", "country": "Country", "city": "City",
  "qs_rank": 50, "acceptance_rate": 20, "tuition_usd": 45000,
  "living_usd": 16000, "duration": "2 years",
  "programs": ["Program 1", "Program 2", "Program 3"],
  "research_areas": ["Area 1", "Area 2"],
  "avg_gre": 320, "avg_gpa": 3.6,
  "placement_rate": 92, "median_salary_usd": 115000,
  "scholarship": "Description",
  "pros": ["Pro 1", "Pro 2", "Pro 3"],
  "cons": ["Con 1", "Con 2"],
  "deadlines": {{"fall": "Dec 15"}},
  "visa_support": "Good",
  "notable_alumni": ["Alumni 1"],
  "type": "Public/Private"
}}"""
    try:
        result = generate(prompt, temperature=0.4)
        parsed = safe_json_parse(result)
        if not parsed:
            return jsonify({"success": False, "error": "Could not parse AI data"})
        return jsonify({"success": True, "data": parsed, "source": "AI Generated"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
