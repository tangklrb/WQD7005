import pymongo
import pandas as pd
from pathlib import Path

mongo_host = "mongodb://localhost:27017/"
mongo_client = pymongo.MongoClient(mongo_host)
db = mongo_client.WQD7005_Assignment

data_directory = '../data/iproperty_listing/'
extract_listing_dir = data_directory + 'extract/listing'
Path(extract_listing_dir).mkdir(parents=True, exist_ok=True)

listings = pd.DataFrame(list(
    db.iproperty_listings.aggregate([
        {
            '$addFields': {
                'price_type': {
                    '$arrayElemAt': [
                        '$prices.type', 0
                    ]
                },
                'price_currency': {
                    '$arrayElemAt': [
                        '$prices.currency', 0
                    ]
                },
                'price_min': {
                    '$arrayElemAt': [
                        '$prices.min', 0
                    ]
                },
                'price_max': {
                    '$arrayElemAt': [
                        '$prices.max', 0
                    ]
                },
                'price_minPricePerSizeUnitByBuiltUp': {
                    '$arrayElemAt': [
                        '$prices.minPricePerSizeUnitByBuiltUp', 0
                    ]
                },
                'price_maxPricePerSizeUnitByBuiltUp': {
                    '$arrayElemAt': [
                        '$prices.maxPricePerSizeUnitByBuiltUp', 0
                    ]
                },
                'price_minPricePerSizeUnitByLandArea': {
                    '$arrayElemAt': [
                        '$prices.minPricePerSizeUnitByLandArea', 0
                    ]
                },
                'price_maxPricePerSizeUnitByLandArea': {
                    '$arrayElemAt': [
                        '$prices.maxPricePerSizeUnitByLandArea', 0
                    ]
                },
                'formatedAddress': '$address.formattedAddress',
                'latitude': '$address.lat',
                'longitude': '$address.lng',
                'state': '$multilanguagePlace.enGB.level1',
                'city': '$multilanguagePlace.enGB.level2',
                'township': '$multilanguagePlace.enGB.level3',
                'attr_bedroom': '$attributes.bedroom',
                'attr_bathroom': '$attributes.bathroom',
                'attr_landArea': '$attributes.landArea',
                'attr_builtUp': '$attributes.builtUp',
                'attr_carPark': '$attributes.carPark',
                'attr_rate': '$attributes.rate',
                'attr_furnishing': '$attributes.furnishing',
                'attr_floorZone': '$attributes.floorZone',
                'attr_governmentRates': '$attributes.governmentRates',
                'attr_buildingAge': '$attributes.buildingAge',
                'attr_outsideArea': '$attributes.outsideArea',
                'attr_maintenanceFee': '$attributes.maintenanceFee',
                'attr_maintenanceFeeByPsf': '$attributes.maintenanceFeeByPsf',
                'attr_layout': '$attributes.layout',
                'attr_landTitleType': '$attributes.landTitleType',
                'attr_tenure': '$attributes.tenure',
                'attr_topYear': '$attributes.topYear',
                'attr_aircond': '$attributes.aircond',
                'attr_pricePSF': '$attributes.pricePSF',
                'attr_pricePerSizeUnit': '$attributes.pricePerSizeUnit',
                'attr_minimumPricePerSizeUnit': '$attributes.minimumPricePerSizeUnit',
                'attr_maximumPricePerSizeUnit': '$attributes.maximumPricePerSizeUnit',
                'attr_facingDirection': '$attributes.facingDirection',
                'attr_unitType': '$attributes.unitType',
                'attr_occupancy': '$attributes.occupancy',
                'attr_titleType': '$attributes.titleType',
                'attr_promotion': '$attributes.promotion',
                'attr_highlight': '$attributes.highlight',
                'attr_sizeUnit': '$attributes.sizeUnit',
                'attr_auctionDate': '$attributes.auctionDate',
                'attr_featureLabel': '$attributes.featureLabel',
                'attr_completionStatus': '$attributes.completionStatus',
                'attr_projectStage': '$attributes.projectStage',
                'attr_bumiDiscount': '$attributes.bumiDiscount',
                'attr_totalUnits': '$attributes.totalUnits',
                'attr_completionDate': '$attributes.completionDate',
                'attr_availableUnits': '$attributes.availableUnits',
                'attr_downloadUrl': '$attributes.downloadUrl',
                'attr_agencyAdvertisingAwardSeal': '$attributes.agencyAdvertisingAwardSeal',
                'attr_agentAdvertisingAwardSeal': '$attributes.agentAdvertisingAwardSeal',
                'attr_developerAdvertisingAwardSeal': '$attributes.developerAdvertisingAwardSeal',
                'attr_youtubeId': '$attributes.youtubeId',
                'attr_threeDUrl': '$attributes.threeDUrl',
                'attr_image360': '$attributes.image360',
                'attr_hasImage360': '$attributes.hasImage360',
                'attr_developerName': '$attributes.developerName',
                'attr_buildYear': '$attributes.buildYear',
                'attr_schoolNetwork': '$attributes.schoolNetwork',
                'attr_projectLicense': '$attributes.projectLicense',
                'attr_projectLicenseValidity': '$attributes.projectLicenseValidity',
                'attr_projectAdvertisingPermit': '$attributes.projectAdvertisingPermit',
                'attr_projectAdvertisingPermitValidity': '$attributes.projectAdvertisingPermitValidity',
                'attr_projectBuildingReferenceNo': '$attributes.projectBuildingReferenceNo',
                'attr_projectApprovalAuthorityBuildingPlan': '$attributes.projectApprovalAuthorityBuildingPlan',
                'attr_projectLandEncumbrance': '$attributes.projectLandEncumbrance',
                'attr_views': '$attributes.views',
                'attr_electricity': '$attributes.electricity',
                'attr_certificate': '$attributes.certificate',
                'attr_propertyCondition': '$attributes.propertyCondition',
                'attr_phoneLine': '$attributes.phoneLine',
                'attr_maidRooms': '$attributes.maidRooms',
                'attr_maidBathroom': '$attributes.maidBathroom',
                'attr_ensuite': '$attributes.ensuite',
                'attr_roomType': '$attributes.roomType',
                'attr_builtYear': '$attributes.builtYear',
                'attr_totalBlocks': '$attributes.totalBlocks',
                'attr_totalFloors': '$attributes.totalFloors',
                'attr_buildingManagement': '$attributes.buildingManagement',
                'attr_floorHeight': '$attributes.floorHeight',
                'attr_characteristicDescription': '$attributes.characteristicDescription',
                'attr_transportDescription': '$attributes.transportDescription',
                'attr_governmentWebsite': '$attributes.governmentWebsite',
                'attr_minimumStay': '$attributes.minimumStay',
                'attr_architectName': '$attributes.architectName',
                'attr_contractorName': '$attributes.contractorName',
                'attr_projectType': '$attributes.projectType',
                'attr_budgetRange': '$attributes.budgetRange',
                'poi_education': {
                    '$size': '$poi.education'
                },
                'poi_healthcare': {
                    '$size': '$poi.healthcare'
                },
                'poi_transportation': {
                    '$size': '$poi.transportation'
                }
            }
        }, {
            '$project': {
                '_id': 0,
                'channels': 0,
                'shareLink': 0,
                'description': 0,
                'isPremiumPlus': 0,
                'cover': 0,
                'medias': 0,
                'floorPlanImages': 0,
                'youtubeIds': 0,
                'updatedAt': 0,
                'postedAt': 0,
                'referenceCode': 0,
                'listerReferenceCode': 0,
                'active': 0,
                'listers': 0,
                'organisations': 0,
                'banner': 0,
                'bankList': 0,
                'prices': 0,
                'multilanguagePlace': 0,
                'address': 0,
                'attributes': 0,
                'poi': 0
            }
        }
    ])
))

# save a copy of the listing extracted
listings.to_csv(extract_listing_dir + '/iproperty_listing.csv.gz', encoding='utf-8', index=False)


