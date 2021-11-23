import scrapy , sys, os ,json

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir =  os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(parent_dir)

class PoliticianSpider(scrapy.Spider):
    name = "politicians"
    base_path="http://www.manthri.lk"
    file_path=parent_dir+"/corpus/"
    profile_id=1
    last_id=1
    names=set([])
    districts=set([])
    parties=set([])
    genders=set([])
    types=set([])
    subjects=set([])
    
    def start_requests(self):

        page_urls=['http://www.manthri.lk/si/politicians']
        for page_num in range(2,10):
            page_urls.append('http://www.manthri.lk/si/politicians?page='+str(page_num))
        for page_url in page_urls:
            yield scrapy.Request(url=page_url, callback=self.parse_page)
        

    def parse_page(self, response):
        profile_num=1
        profile_ref=response.xpath("/html/body/div[2]/div/div[1]/ul[1]/li["+str(profile_num)+"]/h4/a/@href").get()
        while profile_ref is not None:
            profile_url=self.base_path+profile_ref
            yield scrapy.Request(url=profile_url, callback=self.parse_profile)
            self.last_id+=1
            profile_num+=1
            profile_ref=response.xpath("/html/body/div[2]/div/div[1]/ul[1]/li["+str(profile_num)+"]/h4/a/@href").get()
            
                
    def parse_profile(self,response):
        profile={}
        profile["name"]=response.xpath("/html/body/div[2]/section/div/div/div[2]/h1/text()").get().strip()
        profile["party"]=response.xpath("/html/body/div[2]/section/div/div/div[2]/div/p[1]/text()").get().strip()
        profile["district"]=response.xpath("/html/body/div[2]/section/div/div/div[2]/div/p[1]/a/text()").get().strip()
        profile["contact_information"]={}
        phone=response.xpath("/html/body/div[2]/section/div/div/div[2]/div/p[2]/span[1]/text()").get().strip()
        profile["contact_information"]["phone"]= phone.split("/")[0].replace("-","").strip() if "/" in phone else phone.replace("-","")
        email=response.xpath("/html/body/div[2]/section/div/div/div[2]/div/p[2]/span[2]/a/text()").get()
        profile["contact_information"]["email"]=email.strip() if email is not None else "දක්වා නැත"
        birthday=response.xpath("/html/body/div[2]/div/div/div[1]/div[8]/table[1]/tbody/tr[1]/td[2]/text()").get()
        gender=response.xpath("/html/body/div[2]/div/div/div[1]/div[8]/table[1]/tbody/tr[2]/td[2]/text()").get()
        if((birthday is not None) and ("-" in birthday)):
            profile["birthday"]=birthday.strip()
            profile["gender"]=gender.strip() if gender is not None else "දක්වා නැත"
        else:
            profile["birthday"]="දක්වා නැත"
            profile["gender"]=birthday.strip() if birthday is not None else "දක්වා නැත"
        profile["position"]={}
        position=response.xpath("/html/body/div[2]/section/div/div/div[2]/p/text()").get()
        if(position is None):
            profile["position"]["type"]="දක්වා නැත"
            profile["position"]["subject"]="දක්වා නැත"
        elif("-" in position):
            type,subject=position.strip().split("-")
            profile["position"]["type"]=type.strip()
            profile["position"]["subject"]=subject.strip()
        else:
            profile["position"]["type"]=position.strip()
            profile["position"]["subject"]="නැත"

        profile["biography"]=profile["name"]+" "+profile["position"]["subject"]+" "+profile["position"]["type"]+" "+"ය."+" "+"උපන්දිනය"+" "+profile["birthday"]+" "+"ය."+" "+"දුරකථන අංකය සහ විද්‍යුත් තැපෑල පිළිවෙලින්"+" "+profile["contact_information"]["phone"]+" "+profile["contact_information"]["email"]+" "+"වේ."+" "+profile["district"]+" "+"දිස්ත්‍රික්කයෙන්"+" "+profile["party"]+"නියෝජනය කරයි."
        
        with open(self.file_path+str(self.profile_id)+".json", 'w',encoding="utf8") as f:
                json.dump(profile, f,indent = 4,ensure_ascii=False)
         
        self.profile_id+=1

        self.names.add(profile["name"])
        self.districts.add(profile["district"])
        self.parties.add(profile["party"])
        self.genders.add(profile["gender"])
        self.types.add(profile["position"]["type"])
        self.subjects.add(profile["position"]["subject"])


        if(self.profile_id==self.last_id):
            with open(self.file_path+"db.json", 'w',encoding="utf8") as f:
                db={
                    "name":list(self.names),
                    "district":list(self.districts),
                    "party":list(self.parties),
                    "gender":list(self.genders),
                    "position.type":list(self.types),
                    "position.subject":list(self.subjects),
                    }
                json.dump(db, f,indent = 4,ensure_ascii=False)


        
 

    

        

