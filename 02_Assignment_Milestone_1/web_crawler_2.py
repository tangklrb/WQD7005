import re
import sys
import time
import json
import requests
import datetime
import pandas as pd

data_directory = 'data/'
host = 'https://www.iproperty.com.my/'
reaasia_graphql_api = 'https://raptor.rea-asia.com/v1/graphql'
log = open('web_crawler_2.log', 'a+')
max_crawl_retry = 5


def guess_slug_format(input_string):
    return re.sub('[&\/\\#,+()$~%.\'":*?<>{}]', '', re.sub('[‘’“” ]', '-', input_string.strip().lower()))


def crawl_place(level_1_Title=''):
    api = reaasia_graphql_api
    ref_url = host + 'sale/all-residential/'

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
            'level1': level_1_Title,
            'channel': 'sale'
        },
        'query': 'query ($level1: String, $channel: String) {\n  ascLocationSuggestions(level1: $level1, channel: $channel) {\n    items {\n      id\n      type\n      title\n      subtitle\n      label\n      multilanguagePlace {\n        enGB {\n          level1\n          level2\n          level3\n        }\n        msMY {\n          level1\n          level2\n          level3\n        }\n        zhHK {\n          level1\n          level2\n          level3\n        }\n        zhCN {\n          level1\n          level2\n          level3\n        }\n        idID {\n          level1\n          level2\n          level3\n        }\n      }\n    }\n    totalCount\n  }\n}\n'
    }

    level = '1' if level_1_Title == '' else '2 (' + level_1_Title + ')'
    print('Crawl Place: Level', level, 'From:', ref_url, file=log, flush=True)
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
            print('Http Error:', str(errh), '[Retry ' + str(retry_count) + ']')
        except requests.exceptions.ConnectionError as errc:
            print('Error Connecting:', str(errc), '[Retry ' + str(retry_count) + ']')
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', str(errt), '[Retry ' + str(retry_count) + ']')
        except requests.exceptions.RequestException as err:
            print('Unknown Error:', str(err), '[Retry ' + str(retry_count) + ']')
        else:
            return response

    return response


def crawl_listing(place_ids, place_slug, page_token=1):
    api = reaasia_graphql_api
    param_page = '' if page_token == 1 else '?page=' + str(page_token)
    ref_url = host + 'sale/' + place_slug + '/all-residential/' + param_page

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
                'propertyTypes': ['AR'],
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
            'places': [{'level2': place_slug}],
            'pageToken': page_token,
            'pageSize': 20,
            'sortBy': "posted-desc",
            'customTexts': [],
            'placeIds': place_ids,
            'poiIds': [],
            'distance': False,
            'adId': None
        },
        'query': 'query ($channels: [String!], $customTexts: [String], $placeIds: [String], $poiIds: [String], $distance: Int, $sortBy: String, $filters: ListingFilter, $places: [PlaceFilter], $developerId: String, $pageToken: String, $adId: String) {\n  ascListings(channels: $channels, customTexts: $customTexts, placeIds: $placeIds, poiIds: $poiIds, distance: $distance, sortBy: $sortBy, filters: $filters, places: $places, pageSize: 20, pageToken: $pageToken, developerId: $developerId, primaryListingFromSolr: true, adId: $adId) {\n    items {\n      id\n      channels\n      kind\n      shareLink\n      title\n      description\n      subtitle\n      tier\n      isPremiumPlus\n      propertyType\n      color\n      prices {\n        type\n        currency\n        label\n        symbol\n        min\n        max\n        minPricePerSizeUnitByBuiltUp\n        maxPricePerSizeUnitByBuiltUp\n        minPricePerSizeUnitByLandArea\n        maxPricePerSizeUnitByLandArea\n        monthlyPayment\n      }\n      cover {\n        type\n        url\n        urlTemplate\n        width\n        height\n        description\n        thumbnailUrl\n        mimeType\n      }\n      medias {\n        type\n        url\n        urlTemplate\n        width\n        height\n        description\n        thumbnailUrl\n        mimeType\n      }\n      floorPlanImages {\n        type\n        url\n      }\n      youtubeIds\n      updatedAt\n      postedAt\n      address {\n        formattedAddress\n        lat\n        lng\n        hideMarker\n      }\n      referenceCode\n      listerReferenceCode\n      transacted\n      multilanguagePlace {\n        enGB {\n          level1\n          level2\n          level3\n        }\n        zhHK {\n          level1\n          level2\n          level3\n        }\n        zhCN {\n          level1\n          level2\n          level3\n        }\n        idID {\n          level1\n          level2\n          level3\n        }\n        msMY {\n          level1\n          level2\n          level3\n        }\n      }\n      organisations {\n        id\n        type\n        name\n        email\n        license\n        website\n        zendeskId\n        award {\n          media {\n            type\n            url\n            urlTemplate\n            width\n            height\n            description\n            thumbnailUrl\n            mimeType\n          }\n          categories\n          status\n          url\n          type\n        }\n        description\n        estimateListsSize {\n          sale\n          rent\n          new\n        }\n        logo {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        color\n        address {\n          formattedAddress\n          lat\n          lng\n          hideMarker\n        }\n        contact {\n          phones {\n            number\n            label\n          }\n          emails\n          bbms\n        }\n        image {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n      }\n      active\n      attributes {\n        bedroom\n        bathroom\n        landArea\n        builtUp\n        carPark\n        rate\n        furnishing\n        floorZone\n        governmentRates\n        buildingAge\n        outsideArea\n        maintenanceFee\n        maintenanceFeeByPsf\n        layout\n        landTitleType\n        tenure\n        topYear\n        aircond\n        pricePSF\n        pricePerSizeUnit\n        minimumPricePerSizeUnit\n        maximumPricePerSizeUnit\n        facingDirection\n        unitType\n        occupancy\n        titleType\n        promotion\n        highlight\n        sizeUnit\n        auctionDate\n        featureLabel\n        completionStatus\n        projectStage\n        bumiDiscount\n        totalUnits\n        completionDate\n        availableUnits\n        downloadUrl\n        agencyAdvertisingAwardSeal\n        agentAdvertisingAwardSeal\n        developerAdvertisingAwardSeal\n        youtubeId\n        threeDUrl\n        image360\n        hasImage360\n        developerName\n        buildYear\n        schoolNetwork\n        projectLicense\n        projectLicenseValidity\n        projectAdvertisingPermit\n        projectAdvertisingPermitValidity\n        projectBuildingReferenceNo\n        projectApprovalAuthorityBuildingPlan\n        projectLandEncumbrance\n        views\n        electricity\n        certificate\n        propertyCondition\n        phoneLine\n        maidRooms\n        maidBathroom\n        ensuite\n        roomType\n        builtYear\n        totalBlocks\n        totalFloors\n        buildingManagement\n        floorHeight\n        characteristicDescription\n        transportDescription\n        governmentWebsite\n        minimumStay\n        architectName\n        contractorName\n        projectType\n        budgetRange\n      }\n      listers {\n        id\n        type\n        name\n        jobTitle\n        knownLanguages\n        license\n        website\n        award {\n          media {\n            type\n            url\n            urlTemplate\n            width\n            height\n            description\n            thumbnailUrl\n            mimeType\n          }\n          categories\n          status\n          url\n          type\n        }\n        description\n        specificPlace\n        estimateListsSize {\n          sale\n          rent\n          new\n        }\n        image {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        color\n        address {\n          formattedAddress\n          lat\n          lng\n          hideMarker\n        }\n        contact {\n          phones {\n            number\n            label\n          }\n          emails\n          bbms\n        }\n        createdAt\n      }\n      banner {\n        title\n        imageUrl\n        link\n        trackingLink\n        largeImage {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        smallImage {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n      }\n      bankList {\n        data {\n          bank {\n            logo\n            name\n            url\n          }\n          mortgage {\n            interestRate\n            promotionInYear\n            term\n            downPayment\n          }\n        }\n      }\n    }\n    totalCount\n    nextPageToken\n    multilanguagePlaces {\n      enGB {\n        level1\n        level2\n        level3\n      }\n      idID {\n        level1\n        level2\n        level3\n      }\n      zhHK {\n        level1\n        level2\n        level3\n      }\n      zhCN {\n        level1\n        level2\n        level3\n      }\n      msMY {\n        level1\n        level2\n        level3\n      }\n      placeId\n    }\n    locationSpecialists {\n      id\n      type\n      name\n      jobTitle\n      knownLanguages\n      license\n      website\n      award {\n        media {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        categories\n        status\n        url\n        type\n      }\n      description\n      specificPlace\n      estimateListsSize {\n        sale\n        rent\n        new\n      }\n      image {\n        type\n        url\n        urlTemplate\n        width\n        height\n        description\n        thumbnailUrl\n        mimeType\n      }\n      color\n      address {\n        formattedAddress\n        lat\n        lng\n        hideMarker\n      }\n      contact {\n        phones {\n          number\n          label\n        }\n        emails\n        bbms\n      }\n      createdAt\n      organisation {\n        id\n        type\n        name\n        email\n        license\n        website\n        zendeskId\n        award {\n          media {\n            type\n            url\n            urlTemplate\n            width\n            height\n            description\n            thumbnailUrl\n            mimeType\n          }\n          categories\n          status\n          url\n          type\n        }\n        description\n        estimateListsSize {\n          sale\n          rent\n          new\n        }\n        logo {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        color\n        address {\n          formattedAddress\n          lat\n          lng\n          hideMarker\n        }\n        contact {\n          phones {\n            number\n            label\n          }\n          emails\n          bbms\n        }\n        image {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n      }\n    }\n    buildingSpecialists {\n      id\n      type\n      name\n      jobTitle\n      knownLanguages\n      license\n      website\n      award {\n        media {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        categories\n        status\n        url\n        type\n      }\n      description\n      specificPlace\n      estimateListsSize {\n        sale\n        rent\n        new\n      }\n      image {\n        type\n        url\n        urlTemplate\n        width\n        height\n        description\n        thumbnailUrl\n        mimeType\n      }\n      color\n      address {\n        formattedAddress\n        lat\n        lng\n        hideMarker\n      }\n      contact {\n        phones {\n          number\n          label\n        }\n        emails\n        bbms\n      }\n      createdAt\n      organisation {\n        id\n        type\n        name\n        email\n        license\n        website\n        zendeskId\n        award {\n          media {\n            type\n            url\n            urlTemplate\n            width\n            height\n            description\n            thumbnailUrl\n            mimeType\n          }\n          categories\n          status\n          url\n          type\n        }\n        description\n        estimateListsSize {\n          sale\n          rent\n          new\n        }\n        logo {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n        color\n        address {\n          formattedAddress\n          lat\n          lng\n          hideMarker\n        }\n        contact {\n          phones {\n            number\n            label\n          }\n          emails\n          bbms\n        }\n        image {\n          type\n          url\n          urlTemplate\n          width\n          height\n          description\n          thumbnailUrl\n          mimeType\n        }\n      }\n    }\n    administrativeAreas {\n      enGB\n      zhHK\n      zhCN\n    }\n    poiSuggestions {\n      id\n      type\n      title\n      subtitle\n      label\n      multilanguagePlace {\n        enGB {\n          level1\n          level2\n          level3\n        }\n        msMY {\n          level1\n          level2\n          level3\n        }\n        zhHK {\n          level1\n          level2\n          level3\n        }\n        zhCN {\n          level1\n          level2\n          level3\n        }\n        idID {\n          level1\n          level2\n          level3\n        }\n      }\n      additionalInfo {\n        ... on SuggestionAdditionalStationInfo {\n          stops {\n            routeId\n            subType\n            routeColorCode\n            routeDisplaySequence\n            stopIsUnderConstruction\n            stopDisplaySequence\n            routeName {\n              enGB\n              msMY\n              zhHK\n              zhCN\n              idID\n            }\n            isExternalStop\n          }\n          name {\n            enGB\n            msMY\n            zhHK\n            zhCN\n            idID\n          }\n        }\n      }\n    }\n  }\n}\n'
    }

    print('Crawl: Listing(' + str(page_token) + ')', 'From', ref_url, file=log, flush=True)
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
            print('Http Error:', str(errh), '[Retry ' + str(retry_count) + ']')
        except requests.exceptions.ConnectionError as errc:
            print('Error Connecting:', str(errc), '[Retry ' + str(retry_count) + ']')
        except requests.exceptions.Timeout as errt:
            print('Timeout Error:', str(errt), '[Retry ' + str(retry_count) + ']')
        except requests.exceptions.RequestException as err:
            print('Unknown Error:', str(err), '[Retry ' + str(retry_count) + ']')
        else:
            return response

    return response


max_page = 100
print('Program Start:', datetime.datetime.now(), file=log, flush=True)

try:
    while True:
        print(file=log, flush=True)
        session_start_time = datetime.datetime.now()
        print('Page Start:', session_start_time, file=log, flush=True)
        session_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # crawl level 1 places
        response = crawl_place()
        try:
            level_1_places = response['data']['ascLocationSuggestions']['items']
        except:
            e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
            print('Error:', e, file=log, flush=True)
            print('Error: Unable to fetch level 1 places, wait for next round', file=log, flush=True)
            continue

        # if level 1 places is successful
        for level_1 in level_1_places:
            # get each level 1 places title and crawl level 2 places
            try:
                level_1_title = level_1['title'].strip()
                response = crawl_place(level_1_title)
            except:
                e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                print('Error:', e, file=log, flush=True)
                print('Error: Unable to fetch level 1 place title, skip to next level 1 place', file=log, flush=True)
                continue

            # if level 1 places title is successful
            try:
                # crawl level 2 places
                level_2_places = response['data']['ascLocationSuggestions']['items']
            except:
                e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                print('Error:', e, file=log, flush=True)
                print('Error: Unable to fetch level 2 places, skip to next level 1 place', file=log, flush=True)
                continue

            crawl_datetime = pd.read_csv('data/crawl_datetime.csv', delimiter=',')

            # if level 2 places is successful
            for level_2 in level_2_places:
                try:
                    # get details of each level 2 places
                    place_id = level_2['id'].strip()
                    level_2_place_ids = list()
                    level_2_place_ids.append(place_id)
                    level_2_title = level_2['title'].strip()
                    level_2_slug = guess_slug_format(level_2['title'].strip())
                    last_crawl = crawl_datetime[crawl_datetime['id'] == level_2['id'].strip()]
                    last_crawl = last_crawl.iloc[-1] if len(last_crawl) > 0 else None
                    last_crawl_datetime = datetime.datetime.strptime('1900-01-01', "%Y-%m-%d") if last_crawl is None else \
                        datetime.datetime.strptime(last_crawl['last'].strip(), '%Y-%m-%d %H:%M:%S')
                    current_crawl_last = None
                    current_crawl_first = None
                    done = False
                except:
                    e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                    print('Error:', e, file=log, flush=True)
                    print('Error: Unable to fetch level 1 place title, skip to next place', file=log, flush=True)
                    continue

                transaction_ref_url = None
                page_token = 1
                current_listing = list()

                while True:
                    # crawl listing by page
                    response = crawl_listing(level_2_place_ids, level_2_slug, page_token)
                    try:
                        # get current listing page information
                        listing_list = response['data']['ascListings']['items']
                        next_page_token = response['data']['ascListings']['nextPageToken']
                    except:
                        e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                        print('Error:', e, file=log, flush=True)
                        print('Error: Failed to get total page number ', file=log, flush=True)
                        continue

                    # if able to get listing page information
                    for listing in listing_list:
                        try:
                            listing_date = datetime.datetime.strptime(
                                re.sub('[TZtz]', ' ', listing['updatedAt']).strip(), '%Y-%m-%d %H:%M:%S'
                            )
                            if last_crawl_datetime > listing_date:
                                done = True
                            else:
                                current_crawl_last = listing_date if current_crawl_last is None else current_crawl_last
                                current_crawl_first = listing_date
                                current_listing.append(listing)

                        except:
                            page_token = int(page_token) + 1
                            e = str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + str(sys.exc_info()[2])
                            print('Error:', e, file=log, flush=True)
                            print('Error: Failed to fetch listing page', str(page_token), file=log, flush=True)
                            continue

                    if done:
                        break

                    page_token = int(next_page_token) if next_page_token is not None else None
                    if page_token is None or page_token > max_page:
                        break

                # Write listing into file
                with open(data_directory + 'listing_by_place/' + level_2_slug + '_' + str(session_datetime) + '.json',
                          'w') as json_file:
                    json.dump(listing_list, json_file)

                with open('data/crawl_datetime.csv', 'a') as f:
                    f.write(
                        str(place_id) + ',' + str(level_1_title) + ',' + str(level_2_title) + ',' +
                        str(current_crawl_first) + ',' + str(current_crawl_last) + '\n'
                    )

        page_end_time = datetime.datetime.now()
        print('Page Summary:', 'Time Elapsed:', str(page_end_time - page_start_time), file=log, flush=True)
        print('Page End:', str(page_end_time), file=log, flush=True)

        # Next round after 1 hour
        time.sleep(3600)
except KeyboardInterrupt:
    print('Interrupted by user while waiting for next crawl.', file=log, flush=True)

print(file=log, flush=True)
print('Program End:', datetime.datetime.now(), file=log, flush=True)
