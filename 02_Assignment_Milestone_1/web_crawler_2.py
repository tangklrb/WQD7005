import re
import sys
import time
import json
import random
import urllib
import requests
import datetime
from geopy.distance import geodesic
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

data_directory = 'data_2/'
host = 'https://www.iproperty.com.my/'
reaasia_graphql_api = 'https://raptor.rea-asia.com/v1/graphql'
log = open('web_crawler_2.txt', 'a+')
max_crawl_retry = 5


def cool_down(min_sec=1, max_sec=5):
    crawl_interval = random.randint(min_sec * random.randint(2, 3), max_sec * random.randint(4, 5))
    print('Cooldown:', crawl_interval, 'seconds', file=log, flush=True)
    time.sleep(crawl_interval)


def format_url(input_string):
    return re.sub('[&\/\\#,+()$~%.\'":*?<>{}]', '', re.sub('[‘’“” ]', '-', input_string.strip().lower()))


def crawl_condo(page):
    # cool_down(1, 4)
    base_api = 'https://www.iproperty.com.my/condominiums/ajax/ajaxsearchresult?pageno={}&sortby=rating&forsale=&param=/condominiums/search/'
    api = base_api.format(page)
    ref_url = 'https://www.iproperty.com.my/condominiums/search/?sortby=rating'

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'moreFooter=1; _ga=GA1.3.1830955780.1583419839; _gid=GA1.3.1642319135.1583419839; _gcl_au=1.1.1771206039.1583419840; _fbp=fb.2.1583419847670.252004287; __gads=ID=ab744361751fd9f0:T=1583419856:S=ALNI_MZ5NhMtricpdTEXtadsbKEKhQvXUA; scarab.visitor=%222E7741C2F3FCB01B%22; QSI_SI_6W3ggLEHY6kl1mB_intercept=true; ASP.NET_SessionId=gaahuru0fit2u3ut4dln4yrx; AWSELB=297B4D2F1A98A00606AC66C5D972A1C69A40E0A1B1D3AC30DDA194BB5FFEC5351765CBD030125DD224F19CC7DB6CD5F35B5C56717FB5BEB7463E75DE546D947EB6B0A18368; anonymoususerid=795f27ff-635a-4f20-b265-ab7c46d9abe0; _dc_gtm_UA-85157164-4=1; _gat_UA-85157164-4=1; QSI_HistorySession=https%3A%2F%2Fwww.iproperty.com.my%2Fsales%2F~1583419850264%7Chttps%3A%2F%2Fwww.iproperty.com.my%2F~1583419856869%7Chttps%3A%2F%2Fwww.iproperty.com.my%2Fsale%2Fall-residential%2F~1583420016240%7Chttps%3A%2F%2Fwww.iproperty.com.my%2Fcondominiums%2F~1583508758504%7Chttps%3A%2F%2Fwww.iproperty.com.my%2Fcondominiums%2Fsearch%2F%3Fsortby%3Drating~1583508763810',
        'referer': ref_url,
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    print('Crawl: Condominiums Page(' + str(page) + '), From', ref_url, file=log, flush=True)
    retry_count = 0

    while True:
        retry_count = retry_count + 1
        if retry_count >= max_crawl_retry:
            return None

        try:
            request = requests.get(api, headers=headers, timeout=30)
            request.raise_for_status()
            response = request.json()
        except requests.exceptions.HTTPError as errh:
            print('Http Error:', errh, '[Retry ' + retry_count + ']')
        except requests.exceptions.ConnectionError as errc:
            print('Error Connecting:', errc, '[Retry ' + retry_count + ']')
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', errt, '[Retry ' + retry_count + ']')
        except requests.exceptions.RequestException as err:
            print('Unknown Error:', err, '[Retry ' + retry_count + ']')
        else:
            return response

    return response


def crawl_place(condo):
    # cool_down()
    api = reaasia_graphql_api
    ref_url = host + 'sale/' + format_url(condo['PropertyType']) + '/?q=' + urllib.parse.quote(condo['Name'])

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB',
        'content-type': 'application/json',
        'market': 'MY',
        'origin': 'https://www.iproperty.com.my',
        'referer': ref_url,
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'x-market': 'ipropertymy'
    }

    payload = {
        'operationName': None,
        'variables': {
            'channel': 'SALE',
            'query': condo['Name'],
            'administrativeArea': '',
            'maxSuggestions': 50,
            'subTypes': ['LRT', 'BRT', 'MRT', 'KTM KOMUTER', 'MONORAIL', 'ERL']
        },
        'query': 'query ($channel: Channel, $query: String!, $administrativeArea: String!, $maxSuggestions: Int, $types: [String], $subTypes: [String]) {\n  ascSuggestions(channel: $channel, query: $query, administrativeArea: $administrativeArea, maxSuggestions: $maxSuggestions, types: $types, subTypes: $subTypes) {\n    items {\n      id\n      type\n      title\n      subtitle\n      label\n      multilanguagePlace {\n        enGB {\n          level1\n          level2\n          level3\n        }\n        msMY {\n          level1\n          level2\n          level3\n        }\n        zhHK {\n          level1\n          level2\n          level3\n        }\n        zhCN {\n          level1\n          level2\n          level3\n        }\n        idID {\n          level1\n          level2\n          level3\n        }\n      }\n      additionalInfo {\n        ... on SuggestionAdditionalStationInfo {\n          stops {\n            routeId\n            subType\n            routeCode\n            routeColorCode\n            routeDisplaySequence\n            stopIsUnderConstruction\n            stopDisplaySequence\n            routeName {\n              enGB\n              msMY\n              zhHK\n              zhCN\n              idID\n            }\n            isExternalStop\n          }\n          name {\n            enGB\n            msMY\n            zhHK\n            zhCN\n            idID\n          }\n        }\n      }\n    }\n    totalCount\n  }\n}\n'
    }

    print('[B] Crawl: Place Suggestion,', 'From:', ref_url, file=log, flush=True)
    retry_count = 0

    while True:
        retry_count = retry_count + 1

        if retry_count >= max_crawl_retry:
            return None

        try:
            request = requests.post(api, headers=headers, data=json.dumps(payload), timeout=30)
            request.raise_for_status()
            response = request.json()
        except requests.exceptions.HTTPError as errh:
            print('Http Error:', errh, '[Retry ' + retry_count + ']')
        except requests.exceptions.ConnectionError as errc:
            print('Error Connecting:', errc, '[Retry ' + retry_count + ']')
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', errt, '[Retry ' + retry_count + ']')
        except requests.exceptions.RequestException as err:
            print('Unknown Error:', err, '[Retry ' + retry_count + ']')
        else:
            return response

    return response


def crawl_listing(place_ids, ref_url, page_token=1):
    cool_down(1, 3)
    api = reaasia_graphql_api
    param_page = '' if page_token == 1 else '&page=' + str(page_token)
    ref_url = ref_url + param_page

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB',
        'content-type': 'application/json',
        'market': 'MY',
        'origin': 'https://www.iproperty.com.my',
        'referer': ref_url,
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'x-market': 'ipropertymy'
    }

    payload = {
        'operationName': None,
        'variables': {
            'filters': {
                'propertyTypes': [],
                'bedroomRange': {},
                'bathroomRange': {},
                'priceRange': {'min': None, 'max': None},
                'builtupSizeRange': {'min': None, 'max': None},
                'landSizeRange': {},
                'auction': False,
                'transactedIncluded': False,
                'isOwner': False
            },
            'channels': ['sale', 'new'],
            'places': [],
            'pageToken': page_token,
            'pageSize': 20,
            'sortBy': None,
            'customTexts': [],
            'placeIds': place_ids,
            'poiIds': [],
            'distance': False,
            'adId': None
        },
        'query': 'query ($channels: [String!], $customTexts: [String], $placeIds: [String], $poiIds: [String], $distance: Int, $sortBy: String, $filters: ListingFilter, $places: [PlaceFilter], $developerId: String, $pageToken: String, $adId: String) {\n  ascListings(channels: $channels, customTexts: $customTexts, placeIds: $placeIds, poiIds: $poiIds, distance: $distance, sortBy: $sortBy, filters: $filters, places: $places, pageSize: 20, pageToken: $pageToken, developerId: $developerId, primaryListingFromSolr: true, adId: $adId) {\n    items {\n      id\n      channels\n      kind\n      shareLink\n      title\n      description\n      subtitle\n      tier\n      isPremiumPlus\n      propertyType\n      color\n      prices {\n        type\n        currency\n        label\n        symbol\n        min\n        max\n        minPricePerSizeUnitByBuiltUp\n        maxPricePerSizeUnitByBuiltUp\n        minPricePerSizeUnitByLandArea\n        maxPricePerSizeUnitByLandArea\n        monthlyPayment\n      }\n      cover {\n        type\n        url\n        urlTemplate\n        width\n        height\n        description\n        thumbnailUrl\n        mimeType\n      }\n      medias {\n        type\n        url\n        urlTemplate\n        width\n        height\n        description\n        thumbnailUrl\n        mimeType\n      }\n      floorPlanImages {\n        type\n        url\n      }\n      youtubeIds\n      updatedAt\n      postedAt\n      address {\n        formattedAddress\n        lat\n        lng\n        hideMarker\n      }\n      referenceCode\n      listerReferenceCode\n      transacted\n      multilanguagePlace {\n        enGB {\n          level1\n          level2\n          level3\n        }\n        zhHK {\n          level1\n          level2\n          level3\n        }\n        zhCN {\n          level1\n          level2\n          level3\n        }\n        idID {\n          level1\n          level2\n          level3\n        }\n        msMY {\n          level1\n          level2\n          level3\n        }\n      }\n      organisations {\n        id\n        type\n        name\n        email\n        license\n        website\n        zendeskId\n        award {\n          media {\n            type\n            url\n            urlTemplate\n            width\n            height\n            description\n            thumbnailUrl\n            mimeType\n          }\n          categories\n          status\n          url\n          type\n        }\n        description\n        estimateListsSize {\n          sale\n          rent\n          new\n        }\n        logo {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        color\n        address {\n          formattedAddress\n          lat\n          lng\n          hideMarker\n        }\n        contact {\n          phones {\n            number\n            label\n          }\n          emails\n          bbms\n        }\n        image {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n      }\n      active\n      attributes {\n        bedroom\n        bathroom\n        landArea\n        builtUp\n        carPark\n        rate\n        furnishing\n        floorZone\n        governmentRates\n        buildingAge\n        outsideArea\n        maintenanceFee\n        maintenanceFeeByPsf\n        layout\n        landTitleType\n        tenure\n        topYear\n        aircond\n        pricePSF\n        pricePerSizeUnit\n        minimumPricePerSizeUnit\n        maximumPricePerSizeUnit\n        facingDirection\n        unitType\n        occupancy\n        titleType\n        promotion\n        highlight\n        sizeUnit\n        auctionDate\n        featureLabel\n        completionStatus\n        projectStage\n        bumiDiscount\n        totalUnits\n        completionDate\n        availableUnits\n        downloadUrl\n        agencyAdvertisingAwardSeal\n        agentAdvertisingAwardSeal\n        developerAdvertisingAwardSeal\n        youtubeId\n        threeDUrl\n        image360\n        hasImage360\n        developerName\n        buildYear\n        schoolNetwork\n        projectLicense\n        projectLicenseValidity\n        projectAdvertisingPermit\n        projectAdvertisingPermitValidity\n        projectBuildingReferenceNo\n        projectApprovalAuthorityBuildingPlan\n        projectLandEncumbrance\n        views\n        electricity\n        certificate\n        propertyCondition\n        phoneLine\n        maidRooms\n        maidBathroom\n        ensuite\n        roomType\n        builtYear\n        totalBlocks\n        totalFloors\n        buildingManagement\n        floorHeight\n        characteristicDescription\n        transportDescription\n        governmentWebsite\n        minimumStay\n        architectName\n        contractorName\n        projectType\n        budgetRange\n      }\n      listers {\n        id\n        type\n        name\n        jobTitle\n        knownLanguages\n        license\n        website\n        award {\n          media {\n            type\n            url\n            urlTemplate\n            width\n            height\n            description\n            thumbnailUrl\n            mimeType\n          }\n          categories\n          status\n          url\n          type\n        }\n        description\n        specificPlace\n        estimateListsSize {\n          sale\n          rent\n          new\n        }\n        image {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        color\n        address {\n          formattedAddress\n          lat\n          lng\n          hideMarker\n        }\n        contact {\n          phones {\n            number\n            label\n          }\n          emails\n          bbms\n        }\n        createdAt\n      }\n      banner {\n        title\n        imageUrl\n        link\n        trackingLink\n        largeImage {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        smallImage {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n      }\n      bankList {\n        data {\n          bank {\n            logo\n            name\n            url\n          }\n          mortgage {\n            interestRate\n            promotionInYear\n            term\n            downPayment\n          }\n        }\n      }\n    }\n    totalCount\n    nextPageToken\n    multilanguagePlaces {\n      enGB {\n        level1\n        level2\n        level3\n      }\n      idID {\n        level1\n        level2\n        level3\n      }\n      zhHK {\n        level1\n        level2\n        level3\n      }\n      zhCN {\n        level1\n        level2\n        level3\n      }\n      msMY {\n        level1\n        level2\n        level3\n      }\n      placeId\n    }\n    locationSpecialists {\n      id\n      type\n      name\n      jobTitle\n      knownLanguages\n      license\n      website\n      award {\n        media {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        categories\n        status\n        url\n        type\n      }\n      description\n      specificPlace\n      estimateListsSize {\n        sale\n        rent\n        new\n      }\n      image {\n        type\n        url\n        urlTemplate\n        width\n        height\n        description\n        thumbnailUrl\n        mimeType\n      }\n      color\n      address {\n        formattedAddress\n        lat\n        lng\n        hideMarker\n      }\n      contact {\n        phones {\n          number\n          label\n        }\n        emails\n        bbms\n      }\n      createdAt\n      organisation {\n        id\n        type\n        name\n        email\n        license\n        website\n        zendeskId\n        award {\n          media {\n            type\n            url\n            urlTemplate\n            width\n            height\n            description\n            thumbnailUrl\n            mimeType\n          }\n          categories\n          status\n          url\n          type\n        }\n        description\n        estimateListsSize {\n          sale\n          rent\n          new\n        }\n        logo {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        color\n        address {\n          formattedAddress\n          lat\n          lng\n          hideMarker\n        }\n        contact {\n          phones {\n            number\n            label\n          }\n          emails\n          bbms\n        }\n        image {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n      }\n    }\n    buildingSpecialists {\n      id\n      type\n      name\n      jobTitle\n      knownLanguages\n      license\n      website\n      award {\n        media {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        categories\n        status\n        url\n        type\n      }\n      description\n      specificPlace\n      estimateListsSize {\n        sale\n        rent\n        new\n      }\n      image {\n        type\n        url\n        urlTemplate\n        width\n        height\n        description\n        thumbnailUrl\n        mimeType\n      }\n      color\n      address {\n        formattedAddress\n        lat\n        lng\n        hideMarker\n      }\n      contact {\n        phones {\n          number\n          label\n        }\n        emails\n        bbms\n      }\n      createdAt\n      organisation {\n        id\n        type\n        name\n        email\n        license\n        website\n        zendeskId\n        award {\n          media {\n            type\n            url\n            urlTemplate\n            width\n            height\n            description\n            thumbnailUrl\n            mimeType\n          }\n          categories\n          status\n          url\n          type\n        }\n        description\n        estimateListsSize {\n          sale\n          rent\n          new\n        }\n        logo {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        color\n        address {\n          formattedAddress\n          lat\n          lng\n          hideMarker\n        }\n        contact {\n          phones {\n            number\n            label\n          }\n          emails\n          bbms\n        }\n        image {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n      }\n    }\n    administrativeAreas {\n      enGB\n      zhHK\n      zhCN\n    }\n    poiSuggestions {\n      id\n      type\n      title\n      subtitle\n      label\n      multilanguagePlace {\n        enGB {\n          level1\n          level2\n          level3\n        }\n        msMY {\n          level1\n          level2\n          level3\n        }\n        zhHK {\n          level1\n          level2\n          level3\n        }\n        zhCN {\n          level1\n          level2\n          level3\n        }\n        idID {\n          level1\n          level2\n          level3\n        }\n      }\n      additionalInfo {\n        ... on SuggestionAdditionalStationInfo {\n          stops {\n            routeId\n            subType\n            routeColorCode\n            routeDisplaySequence\n            stopIsUnderConstruction\n            stopDisplaySequence\n            routeName {\n              enGB\n              msMY\n              zhHK\n              zhCN\n              idID\n            }\n            isExternalStop\n          }\n          name {\n            enGB\n            msMY\n            zhHK\n            zhCN\n            idID\n          }\n        }\n      }\n    }\n  }\n}\n'
    }

    print('[1] Crawl: Listing(' + str(page_token) + '),', 'From', ref_url, file=log, flush=True)
    retry_count = 0

    while True:
        retry_count = retry_count + 1

        if retry_count >= max_crawl_retry:
            return None

        try:
            request = requests.post(api, headers=headers, data=json.dumps(payload), timeout=30)
            request.raise_for_status()
            response = request.json()
        except requests.exceptions.HTTPError as errh:
            print('Http Error:', errh, '[Retry ' + retry_count + ']')
        except requests.exceptions.ConnectionError as errc:
            print('Error Connecting:', errc, '[Retry ' + retry_count + ']')
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', errt, '[Retry ' + retry_count + ']')
        except requests.exceptions.RequestException as err:
            print('Unknown Error:', err, '[Retry ' + retry_count + ']')
        else:
            return response

    return response


def crawl_poi(condo, category=None, ref_url=None):
    # cool_down()
    api = reaasia_graphql_api
    condo_url = condo['PageUrl1'] if condo['PageUrl2'] is None else condo['PageUrl2']
    ref_url = condo_url if ref_url is None else ref_url

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB',
        'content-type': 'application/json',
        'market': 'MY',
        'origin': 'https://www.iproperty.com.my',
        'referer': ref_url,
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'x-market': 'ipropertymy'
    }

    page_size = 100
    payload = {
        'operationName': None,
        'variables': {
            'lang': 'enGB',
            'location': str(condo['Latitude']) + ',' + str(condo['Longitude']),
            'radius': 3000,
            'pageSize': page_size,
            'category': category
        },
        'query': 'query ($lang: AcceptLanguage, $location: String!, $radius: Int, $pageSize: Int, $category: PoiCategory) {\n  pois(location: $location, radius: $radius, pageSize: $pageSize, category: $category, lang: $lang) {\n    items {\n      name\n      subTypeLabel\n      subTypeExtra\n      geometry {\n        location {\n          lat\n          lng\n          __typename\n        }\n        __typename\n      }\n      subType\n      category\n      lineName\n      placeId\n      distance\n      distanceFloat\n      completionYear\n      type\n      city\n      district\n      publicType\n      curriculumOffered\n      __typename\n    }\n    __typename\n  }\n}\n'
    }

    print('[2] Crawl: POI(' + category + '),', 'From', ref_url, file=log, flush=True)
    retry_count = 0

    while True:
        retry_count = retry_count + 1

        if retry_count >= max_crawl_retry:
            return None

        try:
            request = requests.post(api, headers=headers, data=json.dumps(payload), timeout=30)
            request.raise_for_status()
            response = request.json()
        except requests.exceptions.HTTPError as errh:
            print('Http Error:', errh, '[Retry ' + retry_count + ']')
        except requests.exceptions.ConnectionError as errc:
            print('Error Connecting:', errc, '[Retry ' + retry_count + ']')
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', errt, '[Retry ' + retry_count + ']')
        except requests.exceptions.RequestException as err:
            print('Unknown Error:', err, '[Retry ' + retry_count + ']')
        else:
            return response

    return response


def crawl_transaction(condo, ref_url=None):
    # cool_down()
    api = reaasia_graphql_api
    condo_url = condo['PageUrl1'] if condo['PageUrl2'] is None else condo['PageUrl2']
    ref_url = condo_url if ref_url is None else ref_url

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB',
        'content-type': 'application/json',
        'market': 'MY',
        'origin': 'https://www.iproperty.com.my',
        'referer': ref_url,
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
        'x-market': 'ipropertymy'
    }

    page = 1
    page_size = 200
    payload = {
        'operationName': None,
        'variables': {
            'location1': condo['State'],
            'location2': condo['City'],
            'location3': condo['Name'],
            'block': '',
            'phase': '',
            'lastNthMonth': 0,
            'pageSize': page_size,
            'pageNumber': page,
            'lang': 'enGB',
            'propertyType': condo['PropertyType'],
            'buildingId': condo['Id'],
            'landedType': 'Non-Landed',
            'propertyCategory': condo['LandTitle']
        },
        'query': 'query ($location1: String!, $location2: String!, $location3: String!, $pageSize: Int, $lang: AcceptLanguage, $propertyType: String!, $buildingId: Int, $landedType: String!, $propertyCategory: String!) {\n  transactedData(location1: $location1, location2: $location2, location3: $location3, pageSize: $pageSize, lang: $lang, propertyType: $propertyType, buildingId: $buildingId, landedType: $landedType, propertyCategory: $propertyCategory) {\n    items {\n      address\n      amount\n      bedroom\n      builtUp\n      date\n      floor\n      landArea\n      propertyType\n      psfGross\n      psfNet\n      tenure\n    }\n    meta {\n      location1\n      location2\n      location3\n      title\n      additionalInfo {\n        categoryType\n        psf\n        psfCity\n        psfGrowth\n        rentalYield\n        propertyType\n        comparison\n        lastTransactedDate\n      }\n      totalCount\n    }\n  }\n}\n'
    }

    print('[3] Crawl: Transaction,', 'From', ref_url, file=log, flush=True)
    retry_count = 0

    while True:
        retry_count = retry_count + 1

        if retry_count >= max_crawl_retry:
            return None

        try:
            request = requests.post(api, headers=headers, data=json.dumps(payload), timeout=30)
            request.raise_for_status()
            response = request.json()
        except requests.exceptions.HTTPError as errh:
            print('Http Error:', errh, '[Retry ' + retry_count + ']')
        except requests.exceptions.ConnectionError as errc:
            print('Error Connecting:', errc, '[Retry ' + retry_count + ']')
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', errt, '[Retry ' + retry_count + ']')
        except requests.exceptions.RequestException as err:
            print('Unknown Error:', err, '[Retry ' + retry_count + ']')
        else:
            return response

    return response


print('Program Start:', datetime.datetime.now(), file=log, flush=True)
page = 1
page_to_crawl = 999
page_to_stop = page + page_to_crawl
count_per_page = 20
condo_count = count_per_page * (page - 1) + 1

while True:
    # Crawl Condominiums by page
    page_start_condo_count = condo_count
    page_start_time = datetime.datetime.now()
    print(file=log, flush=True)
    print('Page Start:', page_start_time, file=log, flush=True)

    response = crawl_condo(page)
    try:
        total_pages = int(response['TotalPages'])
        next_page = response['NextPage']
    except:
        page = int(page) + 1
        e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
        print('Failed:', e, file=log, flush=True)
        print('Failed: Skipped and proceed for next page', file=log, flush=True)
        continue

    print('Preparing to crawl:', file=log, flush=True)
    condo_list = list()
    for condo in response['Data']:
        # ==== Step A ===========================================================
        # Search for Individual Condominium's page url format - reverse engineering from javascript
        try:
            condo_id = condo['Id']
            condo_name = condo['Name']
            condo_page_name = format_url(condo_name) + "-" + str(condo_id)
            condo_page_url = host + "condominiums/" + condo_page_name
            condo_property_type = condo['PropertyType']
        except:
            print('Failed:', e, file=log, flush=True)
            print('Failed: Unable to determine Condominium ID, Name or URL. Continue ', file=log, flush=True)
            condo['SalesQueryUrl'] = '-'
            condo['PageName'] = '-'
            condo['PageUrl1'] = '-'
            condo['PageUrl2'] = '-'
        else:
            try:
                condo['SalesQueryUrl'] = host + 'sale/' + format_url(condo_property_type) + '/?q=' + urllib.parse.quote(condo_name)
                condo['PageName'] = condo_page_name
                condo['PageUrl1'] = condo_page_url
                html = urlopen(condo_page_url)
            except HTTPError as e:
                print('Failed:', 'HTTP Error: ' + html.getcode(), file=log, flush=True)
                print('Failed: Unable to determine Condominium URL. Continue ', file=log, flush=True)
                condo['PageUrl2'] = '-'
            except URLError as e:
                print('Failed: Unable to determine Condominium URL. Continue ', file=log, flush=True)
                print('Failed:', 'Server Not Found: ' + html.getcode(), file=log, flush=True)
                condo['PageUrl2'] = '-'
            else:
                condo['PageUrl2'] = html.geturl()

        print('[A] URL Search:', condo_name, '[Formulated]', condo['PageUrl1'], file=log, flush=True)
        print('[A] URL Search:', condo_name, '[Redirected]', condo['PageUrl2'], file=log, flush=True)

        # Individual Condominium's most relevant placeID
        condo_suggested_place_id = list()
        # ==== Step B ===========================================================
        # Crawl for PlaceID using Condominium's Name from Place Suggestion
        place_suggestion = crawl_place(condo)
        try:
            condo_city = '' if condo['City'] is None else condo['City'].strip().lower()
            condo_state = '' if condo['State'] is None else condo['State'].strip().lower()
            place_list = place_suggestion['data']['ascSuggestions']['items']
        except:
            # Skipping saving Place Suggestion to file
            e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
            print('Failed:', e, file=log, flush=True)
            print('Failed: Skipped and proceed for next step', file=log, flush=True)
        else:
            # Write Place Suggestions to file
            with open(data_directory + 'place/' + condo_page_name + '.json', 'w') as json_file:
                json.dump(place_list, json_file)

            for place in place_list:
                try:
                    place_type = place['type'].strip().lower()
                    if not place_type == 'property':
                        continue

                    place_city = place['multilanguagePlace']['enGB']['level2'].strip().lower()
                    place_state = place['multilanguagePlace']['enGB']['level1'].strip().lower()
                    place_id = place['id'].strip().lower()

                    if condo_city == place_city and condo_state == place_state:
                        condo_suggested_place_id.append(place_id)
                except:
                    e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                    print('Failed:', e, file=log, flush=True)
                    print('Failed: Skipped and proceed for next suggested place', file=log, flush=True)
                    continue

        condo['PlaceId'] = condo_suggested_place_id
        condo_list.append(condo)
        print('[B] Place Search:', condo_name, json.dumps(condo['PlaceId']), file=log, flush=True)

    print(file=log, flush=True)

    # Write current crawled Condominium list to file
    with open(data_directory + 'condominium/page~' + str(page) + '.json', 'w') as json_file:
        json.dump(condo_list, json_file)

    for condo in condo_list:
        condo_name = condo['Name']
        condo_page_name = condo['PageName']
        condo_suggested_place_id = condo['PlaceId']
        condo_city = '' if condo['City'] is None else condo['City']
        condo_state = '' if condo['State'] is None else condo['State']
        condo_township = '' if condo['Township'] is None else condo['Township']
        listing_ref_url = condo['SalesQueryUrl']
        print('Condo [' + str(condo_count) + '=' + condo_name + '] Start:', datetime.datetime.now(), file=log, flush=True)

        # ==== Step 1 ===========================================================
        # Crawl for listing using PlaceID of the best matched Place Suggestion as query string
        transaction_ref_url = None
        page_token = 1
        while True:
            response = crawl_listing(condo_suggested_place_id, listing_ref_url, page_token)
            try:
                listing_list = response['data']['ascListings']['items']
                total_listing = int(response['data']['ascListings']['totalCount'])
                next_page_token = response['data']['ascListings']['nextPageToken']
            except:
                page_token = int(page_token) + 1
                e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                print('Failed:', e, file=log, flush=True)
                print('Failed: Skipped and proceed for next listing page', file=log, flush=True)
                continue

            # Write listing into file
            with open(data_directory + 'listing/' + condo_page_name + '~' + str(page_token) + '.json', 'w') as json_file:
                json.dump(listing_list, json_file)

            # Find a matching listing, for reference URL usage in crawling POI and Transaction
            if transaction_ref_url is None:
                for listing in listing_list:
                    try:
                        listing_latitude = listing['address']['lat']
                        listing_longitude = listing['address']['lng']
                        listing_coordinate = (listing_latitude, listing_longitude)
                        condo_latitude = condo['Latitude']
                        condo_longitude = condo['Longitude']
                        condo_coordinate = (condo_latitude, condo_longitude)
                        distance = geodesic(listing_coordinate, condo_coordinate).meters
                        prefix = host + 'property/' + format_url(condo_city) + '/' + format_url(condo_name)
                        prefix = re.sub('[-@]', '', prefix)
                        listing_title = listing['title']
                        listing_test_url = re.sub('[-@]', '', listing['shareLink'])
                        condo_title = condo_name + ", " + condo_city if condo_township == '' \
                            else condo_name + ", " + condo_township + ", " + condo_city

                        print('Listing Matching:', listing_test_url, 'vs', file=log, flush=True)
                        print('Listing Matching:', prefix, file=log, flush=True)
                        print('Listing Matching:', listing_title, 'vs', condo_name + ", " + condo_city,
                              file=log, flush=True)
                        print('Listing Matching:',
                              '(' + str(listing_latitude) + ', ' + str(listing_longitude) + ')',
                              'vs', '(' + str(condo_latitude) + ', ' + str(condo_longitude) + ')',
                              '=', distance, file=log, flush=True)

                        if (listing_test_url.startswith(prefix)) \
                                or (listing_title == condo_title and (distance < 25)):
                            print('Listing Matching: Success', file=log, flush=True)
                            transaction_ref_url = listing['shareLink']
                            break

                    except:
                        e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                        print('Failed:', e, file=log, flush=True)
                        print('Failed: Cannot find listing as referral URL, use Condominium page URL', file=log, flush=True)

            page_token = next_page_token
            if page_token is None:
                break

        # ==== Step 2 ===========================================================
        # Crawl for POI using Condominium's geo location
        # Crawl only once for each condominium, need to pass in a matching listing url as reference
        poi_categories = ['education', 'healthcare', 'transportation']
        poi_list = list()

        for category in poi_categories:
            response = crawl_poi(condo, category, transaction_ref_url)
            try:
                poi_list = poi_list + response['data']['pois']['items']
            except:
                e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                print('Failed:', e, file=log, flush=True)
                print('Failed: Skipped and proceed for next POI category', file=log, flush=True)
                continue

        # Write Transactions into file
        with open(data_directory + 'poi/' + condo_page_name + '.json', 'w+') as json_file:
            json.dump(poi_list, json_file)

        # ==== Step 3 ===========================================================
        # Crawl for Transaction records of each Condominium
        # Crawl only once for each condominium, need to pass in a matching listing url as reference

        response = crawl_transaction(condo, transaction_ref_url)
        try:
            transaction_list = response['data']['transactedData']['items']
            investment = response['data']['transactedData']['meta']
            investment['condo_page_name'] = condo_page_name
        except:
            e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
            print('Failed:', e, file=log, flush=True)
            print('Failed: Skipped and proceed for next step', file=log, flush=True)
        else:
            # Write Transactions into file
            with open(data_directory + 'transaction/' + condo_page_name + '.json', 'w') as json_file:
                json.dump(transaction_list, json_file)

            with open(data_directory + 'investment/' + condo_page_name + '.json', 'w') as json_file:
                json.dump(investment, json_file)

        print('Condo [' + str(condo_count) + '=' + condo_name + '] End:', datetime.datetime.now(), file=log, flush=True)
        condo_count = condo_count + 1
        print(file=log, flush=True)

    page_end_time = datetime.datetime.now()
    print('Page Summary:', 'Condominiums Crawled:', str(condo_count - page_start_condo_count), file=log, flush=True)
    print('Page Summary:', 'Time Elapsed:', page_end_time - page_start_time, file=log, flush=True)
    print('Page End:', page_end_time, file=log, flush=True)
    page = next_page

    if page is None or page > total_pages or page > page_to_stop:
        break

print(file=log, flush=True)
print('Program End:', datetime.datetime.now(), file=log, flush=True)
