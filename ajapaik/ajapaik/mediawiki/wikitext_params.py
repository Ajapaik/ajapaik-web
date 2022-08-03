
def get_external_id(p):
    if p.external_id and p.external_id.strip():
        external_id=p.external_id
    elif p.source_url and ('urn:' in p.source_url or 'URN:' in p.source_url) and 'http' not in p.source_url :
        external_id=p.source_url
    else:
        external_id=''

    return external_id

def get_date_text(p):
    if p.date_text:
        date_text=p.date_text
    elif p.date:
        date_text=p.date.strftime('%Y-%m-%d')
    else:
        date_text=''
    return date_text

def get_source_text(p, ajapaik_url):
    if p.source_url and 'http' in p.source_url:
        source_url=p.source_url
    else:
        source_url=ajapaik_url

    if external_id:
        source_text='[' + source_url + ' ' + external_id +']'
    else:
        source_text=source_url
    return source_text

def get_author_text(p):
    if p.rephoto_of_id:
        pp=p.rephoto_of   
        author_text=p.user.get_display_name
    else:
        pp=p
        author_text=pp.author
    return author_text

def get_description_text(p):
    if p.rephoto_of_id:
        pp=p.rephoto_of   
    else:
        pp=p

    if p.rephoto_of_id:
        if p.description:
            description_text=p.description 
        elif pp.description:
            description_text='historical photo description: ' +  pp.description 
        elif p.title:
            description_text=p.title
        elif pp.title:
            description_text='historical photo title: ' +  pp.title
        else:
            description_text=''
    else:
        description_text=p.description or p.title or ''
    return description_text


def get_commons_filename(p, external_id, date_text):
    if p.rephoto_of_id:
        pp=p.rephoto_of   
    else:
        pp=p

    if pp.title:
        commons_filename=pp.title[:50] 
    elif pp.description:
        commons_filename=pp.description[:50]
    else:
        commons_filename='no name give'

    if p.rephoto_of_id:
        commons_filename="Rephoto of " + commons_filename 

    if external_id:
        commons_filename=commons_filename + '_-_' + external_id
    else:
        commons_filename=commons_filename + '_-_' + date_text

    commons_filename=commons_filename.replace('.', '_')
    commons_filename=commons_filename.replace(':', '_')
    commons_filename=commons_filename.replace(' ', '_')
    commons_filename=re.sub('_+', '_', commons_filename)

    return commons_filename

def get_location_template(p, ajapaik_url):
    if p.lat and p.lon and p.azimuth:
        if p.azimuth < 0:
            location_template='{{Location|' + str(p.lat) + '|' + str(p.lon) + '|heading:' + str(360-p.azimuth) + ' source:'+ajapaik_url+'}}' 
        else:
            location_template='{{Location|' + str(p.lat) + '|' + str(p.lon) + '|heading:' + str(p.azimuth) + ' source:'+ajapaik_url+'}}' 
    elif p.lat and p.lon:
        location_template='{{Location|' + str(p.lat) + '|' + str(p.lon) +'|source:'+ajapaik_url+' }}'
    elif pp.lat and pp.lon and pp.azimuth:
        if pp.azimuth < 0:
            location_template='{{Location|' + str(pp.lat) + '|' + str(pp.lon) + '|heading:' + str(360-pp.azimuth) + ' source:'+ajapaik_url+'}}' 
        else:
            location_template='{{Location|' + str(pp.lat) + '|' + str(pp.lon) + '|heading:' + str(pp.azimuth) + ' source:'+ajapaik_url+'}}' 
    elif pp.lat and pp.lon:
        location_template='{{Location|' + str(pp.lat) + '|' + str(pp.lon) +'|source:'+ajapaik_url+' }}'
    else:
        location_template='' 
    return location_template

def get_address_text(p):
    if p.rephoto_of_id:
        pp=p.rephoto_of   
    else:
        pp=p

    if p.address:
        address_text='; ' + p.address
    elif pp.address:
        address_text='; ' + pp.address
    else:
        address_text=''

    return address_text

def get_ajapaik_photo_wikitext_params(p):
    ajapaik_url='https://ajapaik.ee/photo/' + str(p.id)
    external_id=get_external_id_text(p)
    date_text=get_date_text(p)

    licence_text=get_licence_template(p.licence.url)
    if not licence_text:
        return False

    out={}
    out["licence"]=get_licence_template(p.licence.url)
    out["description"]=get_description_text(p)
    out["author"]=get_author_text(p)
    out["date"]=date_text
    out["place"]=get_address_text(p)
    out["institution"]=""
    out["year_category"]=""
    out["source"]=get_source_text(p, ajapaik_url)
    out["identifierString"]=external_id
    out["footer_template"]=""
    out["location_template"]=get_location_template(p, ajapaik_url)
    out["commons_filename"]=get_commons_filename(p, external_id, date_text)
    out["source_filename"]='media/' + str(p.image)
    out["ajapaik_url"]=ajapaik_url
    out["comment"]="Uploading " + ajapaik_url
    return out


