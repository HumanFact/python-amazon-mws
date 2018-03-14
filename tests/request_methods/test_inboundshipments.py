"""
Tests for the InboundShipments API class.
"""
import datetime
import unittest
import mws
from mws.apis.inbound_shipments import parse_item_args
from mws.mws import MWSError
from .utils import CommonRequestTestTools


class ParseItemArgsTestCase(unittest.TestCase):
    """
    Test cases that ensure `parse_item_args` raises exceptions where appropriate.
    """
    def test_empty_args_list(self):
        """
        Should raise `MWSError` for an empty set of arguments.
        """
        item_args = []
        operation = 'dummy'
        with self.assertRaises(MWSError):
            parse_item_args(item_args, operation)

    def test_item_not_a_dict(self):
        """
        Should raise `MWSError` if item arguments are not all dict objects
        """
        item_args = ['this is not a dict']
        operation = 'dummy'
        with self.assertRaises(MWSError):
            parse_item_args(item_args, operation)

    def test_required_keys_missing_CreateInboundShipmentPlan(self):
        """
        Should raise `MWSError` if a required key is missing from at least one item dict
        for the CreateInboundShipmentPlan operation
        """
        operation = 'CreateInboundShipmentPlan'
        # SKU missing
        item_args_1 = [
            {
                'quantity': 34,
            },
        ]
        with self.assertRaises(MWSError):
            parse_item_args(item_args_1, operation)
        # Quantity missing
        item_args_2 = [
            {
                'sku': 'something',
            },
        ]
        with self.assertRaises(MWSError):
            parse_item_args(item_args_2, operation)

    def test_required_keys_missing_other_operation(self):
        """
        Should raise `MWSError` if a required key is missing from at least one item dict
        for operations other than CreateInboundShipmentPlan.
        """
        operation = 'other operation'
        # SKU missing
        item_args_1 = [
            {
                'quantity': 56,
            },
        ]
        with self.assertRaises(MWSError):
            parse_item_args(item_args_1, operation)
        # Quantity missing
        item_args_2 = [
            {
                'sku': 'soemthingelse',
            },
        ]
        with self.assertRaises(MWSError):
            parse_item_args(item_args_2, operation)

    def test_args_built_CreateInboundShipmentPlan(self):
        """
        Item args should build successfully for the CreateInboundShipmentPlan operation.
        """
        operation = 'CreateInboundShipmentPlan'
        # SKU missing
        item_args = [
            {
                'sku': 'somethingelse',
                'quantity': 56,
                'quantity_in_case': 12,
                'asin': 'ANYTHING',
                'condition': 'Used',
            },
            {
                'sku': 'something',
                'quantity': 34,
            },
        ]
        parsed_items = parse_item_args(item_args, operation)
        expected = [
            {
                'SellerSKU': 'somethingelse',
                'Quantity': 56,
                'QuantityInCase': 12,
                'ASIN': 'ANYTHING',
                'Condition': 'Used',
            },
            {
                'SellerSKU': 'something',
                'Quantity': 34,
                'QuantityInCase': None,
                'ASIN': None,
                'Condition': None,
            },
        ]
        self.assertEqual(parsed_items[0], expected[0])
        self.assertEqual(parsed_items[1], expected[1])

    def test_args_built_other_operation(self):
        """
        Item args should build successfully for operations other than CreateInboundShipmentPlan.
        """
        operation = 'other_operation'
        # SKU missing
        item_args = [
            {
                'sku': 'one_thing',
                'quantity': 34,
                'quantity_in_case': 5,
            },
            {
                'sku': 'the_other_thing',
                'quantity': 7,
            },
        ]
        parsed_items = parse_item_args(item_args, operation)
        expected = [
            {
                'SellerSKU': 'one_thing',
                'QuantityShipped': 34,
                'QuantityInCase': 5,
            },
            {
                'SellerSKU': 'the_other_thing',
                'QuantityShipped': 7,
                'QuantityInCase': None,
            },
        ]
        self.assertEqual(parsed_items[0], expected[0])
        self.assertEqual(parsed_items[1], expected[1])


class SetShipFromAddressTestCase(unittest.TestCase):
    """
    Test case covering msw.InboundShipments.set_ship_from_address
    """
    def setUp(self):
        self.inbound = mws.InboundShipments('', '', '')

    def test_address_empty_raises_exception(self):
        """
        Empty address dict should raise MWSError.
        """
        address = {}
        with self.assertRaises(MWSError):
            self.inbound.set_ship_from_address(address)

    def test_address_not_dict_raises_exception(self):
        """
        Non-dict argument should raise MWSError.
        """
        address = 'this is not a dict'
        with self.assertRaises(MWSError):
            self.inbound.set_ship_from_address(address)

    def test_required_keys_missing(self):
        """
        Any missing required key should raise MWSError
        """
        # Missing name
        address_1 = {
            'address_1': '500 Summat Cully Lane',
            'city': 'Gilead',
        }
        # Missing address_1 (address line 1)
        address_2 = {
            'name': 'Roland Deschain',
            'city': 'Gilead',
        }
        # Missing city
        address_3 = {
            'name': 'Roland Deschain',
            'address_1': '500 Summat Cully Lane',
        }
        with self.assertRaises(MWSError):
            self.inbound.set_ship_from_address(address_1)
        with self.assertRaises(MWSError):
            self.inbound.set_ship_from_address(address_2)
        with self.assertRaises(MWSError):
            self.inbound.set_ship_from_address(address_3)

    def test_full_address_built_properly(self):
        """
        An address with all fields covered should be contructed properly.
        """
        address = {
            'name': 'Roland Deschain',
            'address_1': '500 Summat Cully Lane',
            'address_2': 'Apartment 19',
            'city': 'Gilead',
            'district_or_county': 'West-Town',
            'state_or_province': 'New Canaan',
            'postal_code': '13019',
            'country': 'Mid-World',
        }
        self.inbound.set_ship_from_address(address)
        expected = {
            'ShipFromAddress.Name': 'Roland Deschain',
            'ShipFromAddress.AddressLine1': '500 Summat Cully Lane',
            'ShipFromAddress.AddressLine2': 'Apartment 19',
            'ShipFromAddress.City': 'Gilead',
            'ShipFromAddress.DistrictOrCounty': 'West-Town',
            'ShipFromAddress.StateOrProvinceCode': 'New Canaan',
            'ShipFromAddress.PostalCode': '13019',
            'ShipFromAddress.CountryCode': 'Mid-World',
        }
        self.assertEqual(self.inbound.from_address, expected)

    def test_partial_address_built_properly(self):
        """
        An address with only required fields covered should be contructed properly,
        with ommitted keys filled in with defaults.
        """
        address = {
            'name': 'Roland Deschain',
            'address_1': '500 Summat Cully Lane',
            'city': 'Gilead',
        }
        self.inbound.set_ship_from_address(address)
        expected = {
            'ShipFromAddress.Name': 'Roland Deschain',
            'ShipFromAddress.AddressLine1': '500 Summat Cully Lane',
            'ShipFromAddress.AddressLine2': None,
            'ShipFromAddress.City': 'Gilead',
            'ShipFromAddress.DistrictOrCounty': None,
            'ShipFromAddress.StateOrProvinceCode': None,
            'ShipFromAddress.PostalCode': None,
            'ShipFromAddress.CountryCode': 'US',
        }
        self.assertEqual(self.inbound.from_address, expected)

    def test_set_address_with_constructor(self):
        """
        An address passed to the InboundShipments constructor as a `from_address` kwarg
        should automatically set the `from_address` attribute accordingly.
        (Ignoring the self.inbound attribute in this case.)
        """
        address = {
            'name': 'Roland Deschain',
            'address_1': '500 Summat Cully Lane',
            'city': 'Gilead',
        }
        inbound_constructed = mws.InboundShipments('', '', '', from_address=address)
        expected = {
            'ShipFromAddress.Name': 'Roland Deschain',
            'ShipFromAddress.AddressLine1': '500 Summat Cully Lane',
            'ShipFromAddress.AddressLine2': None,
            'ShipFromAddress.City': 'Gilead',
            'ShipFromAddress.DistrictOrCounty': None,
            'ShipFromAddress.StateOrProvinceCode': None,
            'ShipFromAddress.PostalCode': None,
            'ShipFromAddress.CountryCode': 'US',
        }
        self.assertEqual(inbound_constructed.from_address, expected)


# class FBAShipmentHandlingTestCase(unittest.TestCase, CommonRequestTestTools):
#     """
#     Test cases for InboundShipments involving FBA shipment handling.
#     These cases require `from_address` to be set, while others do not.
#     """
#     # TODO Fill in later.
#     def setUp(self):
#         addr = {
#             'name': 'Roland Deschain',
#             'address_1': '500 Summat Cully Lane',
#             'city': 'Gilead',
#         }
#         self.api = mws.InboundShipments(
#             self.CREDENTIAL_ACCESS,
#             self.CREDENTIAL_SECRET,
#             self.CREDENTIAL_ACCOUNT,
#             auth_token=self.CREDENTIAL_TOKEN,
#             from_address=addr,
#         )
#         self.api._test_request_params = True

#     def test_create_inbound_shipment_plan_exceptions(self):
#         """
#         Covers cases that should raise exceptions for the `create_inbound_shipment_plan` method.
#         """
#         pass

#     def test_create_inbound_shipment_plan(self):
#         """
#         Covers successful data entry for `create_inbound_shipment_plan`.
#         """
#         pass

#     def test_create_inbound_shipment_exceptions(self):
#         """
#         Covers cases that should raise exceptions for the `create_inbound_shipment` method.
#         """
#         pass

#     def test_create_inbound_shipment(self):
#         """
#         Covers successful data entry for `create_inbound_shipment`.
#         """
#         pass

#     def test_update_inbound_shipment_exceptions(self):
#         """
#         Covers cases that should raise exceptions for the `update_inbound_shipment` method.
#         """
#         pass

#     def test_update_inbound_shipment(self):
#         """
#         Covers successful data entry for `update_inbound_shipment`.
#         """
#         pass


class InboundShipmentsRequestsTestCase(unittest.TestCase, CommonRequestTestTools):
    """
    Test cases for InboundShipments requests that do not involve FBA shipment handling
    and do not require `from_address` to be set.
    """
    def setUp(self):
        self.api = mws.InboundShipments(
            self.CREDENTIAL_ACCESS,
            self.CREDENTIAL_SECRET,
            self.CREDENTIAL_ACCOUNT,
            auth_token=self.CREDENTIAL_TOKEN
        )
        self.api._test_request_params = True

    def test_get_inbound_guidance_for_sku(self):
        """
        GetInboundGuidanceForSKU operation.
        """
        marketplace_id = 'eyuMuohmyP'
        # Case 1: list of SKUs
        sku_list_1 = [
            '5PWmAy4u1A',
            'CtwNnGX08l',
        ]
        params_1 = self.api.get_inbound_guidance_for_sku(
            skus=sku_list_1,
            marketplace_id=marketplace_id,
        )
        self.assert_common_params(params_1)
        self.assertEqual(params['Action'], 'GetInboundGuidanceForSKU')
        self.assertEqual(params['MarketplaceId'], marketplace_id)
        self.assertEqual(params['SellerSKUList.Id.1'], sku_list_1[0])
        self.assertEqual(params['SellerSKUList.Id.2'], sku_list_1[1])
        # Case 2: single SKU
        sku_list_2 = '9QWsksBUMI'
        params_2 = self.api.get_inbound_guidance_for_sku(
            skus=sku_list_2,
            marketplace_id=marketplace_id,
        )
        self.assert_common_params(params_2)
        self.assertEqual(params['Action'], 'GetInboundGuidanceForSKU')
        self.assertEqual(params['MarketplaceId'], marketplace_id)
        self.assertEqual(params['SellerSKUList.Id.1'], sku_list_2)

    def test_get_inbound_guidance_for_asin(self):
        """
        GetInboundGuidanceForASIN operation.
        """
        marketplace_id = 'osnufVjvfR'
        # Case 1: list of SKUs
        asin_list_1 = [
            'I2HCJMQ1sB',
            'EBDjm91glL',
        ]
        params_1 = self.api.get_inbound_guidance_for_asin(
            asins=asin_list_1,
            marketplace_id=marketplace_id,
        )
        self.assert_common_params(params_1)
        self.assertEqual(params['Action'], 'GetInboundGuidanceForASIN')
        self.assertEqual(params['MarketplaceId'], marketplace_id)
        self.assertEqual(params['ASINList.Id.1'], asin_list_1[0])
        self.assertEqual(params['ASINList.Id.2'], asin_list_1[1])
        # Case 2: single SKU
        asin_list_2 = 'FW2e9soodD'
        params_2 = self.api.get_inbound_guidance_for_asin(
            asins=asin_list_2,
            marketplace_id=marketplace_id,
        )
        self.assert_common_params(params_2)
        self.assertEqual(params['Action'], 'GetInboundGuidanceForASIN')
        self.assertEqual(params['MarketplaceId'], marketplace_id)
        self.assertEqual(params['ASINList.Id.1'], asin_list_2)

    def test_get_preorder_info(self):
        """
        GetPreorderInfo operation.
        """
        shipment_id = 'oYRjQbGLL6'
        params = self.api.get_preorder_info(shipment_id)
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'GetPreorderInfo')
        self.assertEqual(params['ShipmentId'], shipment_id)

    def test_confirm_preorder(self):
        """
        ConfirmPreorder operation.
        """
        shipment_id = 'H4UiUjY7Fr'
        need_by_date = datetime.datetime.utcnow()
        params = self.api.confirm_preorder(
            shipment_id=shipment_id,
            need_by_date=need_by_date,
        )
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'ConfirmPreorder')
        self.assertEqual(params['ShipmentId'], shipment_id)
        self.assertEqual(params['NeedByDate'], need_by_date.isoformat())

    def test_get_prep_instructions_for_sku(self):
        """
        GetPrepInstructionsForSKU operation.
        """
        # Case 1: simple list
        skus_1 = [
            'ZITw0KqI3W',
            'qLijuY05j7',
        ]
        country_code = 'Wakanda'
        params_1 = self.api.get_prep_instructions_for_sku(
            skus=skus_1,
            country_code=country_code,
        )
        self.assert_common_params(params_1)
        self.assertEqual(params_1['Action'], 'GetPrepInstructionsForSKU')
        self.assertEqual(params_1['ShipToCountryCode'], country_code)
        self.assertEqual(params_1['SellerSKUList.ID.1'], skus_1[0])
        self.assertEqual(params_1['SellerSKUList.ID.2'], skus_1[1])
        # Case 2: duplicates should be removed before creating params,
        # with their ordering preserved.
        skus_2 = [
            'pvHENgh9GG',
            'yrFQfk66Ku',
            'pvHENgh9GG',  # duplicate should be removed in param build
            '3W2DgshBxW',
            'FBN4E7FK3S',
        ]
        params_2 = self.api.get_prep_instructions_for_sku(
            skus=skus_2,
            country_code=country_code,
        )
        self.assert_common_params(params_2)
        self.assertEqual(params_2['Action'], 'GetPrepInstructionsForSKU')
        self.assertEqual(params_2['ShipToCountryCode'], country_code)
        self.assertEqual(params_2['SellerSKUList.ID.1'], skus_2[0])
        self.assertEqual(params_2['SellerSKUList.ID.2'], skus_2[1])
        # skus_2[2] is a duplicate and should not be expected. skus_2[3] is next unique.
        self.assertEqual(params_2['SellerSKUList.ID.3'], skus_2[3])
        self.assertEqual(params_2['SellerSKUList.ID.4'], skus_2[4])

    def test_get_prep_instructions_for_asin(self):
        """
        GetPrepInstructionsForASIN operation.
        """
        # Case 1: simple list
        asins_1 = [
            'iTgHUxF1a7',
            '56gwMz7j1N',
        ]
        country_code = 'Wakanda'
        params_1 = self.api.get_prep_instructions_for_asin(
            asins=asins_1,
            country_code=country_code,
        )
        self.assert_common_params(params_1)
        self.assertEqual(params_1['Action'], 'GetPrepInstructionsForASIN')
        self.assertEqual(params_1['ShipToCountryCode'], country_code)
        self.assertEqual(params_1['ASINList.ID.1'], asins_1[0])
        self.assertEqual(params_1['ASINList.ID.2'], asins_1[1])
        # Case 2: duplicates should be removed before creating params,
        # with their ordering preserved.
        asins_2 = [
            'FCYeaVUYqY',
            'bma5ysgs8E',
            'IwyBQG9TgX',
            'IwyBQG9TgX',  # duplicate should be removed in param build
            'JPA8CyPAOF',
        ]
        params_2 = self.api.get_prep_instructions_for_asin(
            asins=asins_2,
            country_code=country_code,
        )
        self.assert_common_params(params_2)
        self.assertEqual(params_2['Action'], 'GetPrepInstructionsForASIN')
        self.assertEqual(params_2['ShipToCountryCode'], country_code)
        self.assertEqual(params_2['ASINList.ID.1'], asins_2[0])
        self.assertEqual(params_2['ASINList.ID.2'], asins_2[1])
        self.assertEqual(params_2['ASINList.ID.3'], asins_2[2])
        # asins_2[3] is a duplicate and should not be expected. asins_2[4] is next unique.
        self.assertEqual(params_2['ASINList.ID.4'], asins_2[4])

    # def test_put_transport_content(self):
    #     """
    #     PutTransportContent operation.
    #     """
    #     pass

    def test_estimate_transport_request(self):
        """
        EstimateTransportRequest operation.
        """
        shipment_id = 'w6ayzk2Aov'
        params = self.api.estimate_transport_request(shipment_id)
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'EstimateTransportRequest')
        self.assertEqual(params['ShipmentId'], shipment_id)

    def test_get_transport_content(self):
        """
        GetTransportContent operation.
        """
        shipment_id = 'w6ayzk2Aov'
        params = self.api.get_transport_content(shipment_id)
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'GetTransportContent')
        self.assertEqual(params['ShipmentId'], shipment_id)

    def test_confirm_transport_request(self):
        """
        ConfirmTransportRequest operation.
        """
        shipment_id = 'UTULruKM6v'
        params = self.api.confirm_transport_request(shipment_id)
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'ConfirmTransportRequest')
        self.assertEqual(params['ShipmentId'], shipment_id)

    def test_void_transport_request(self):
        """
        VoidTransportRequest operation.
        """
        shipment_id = 'bJw9pyKcoB'
        params = self.api.void_transport_request(shipment_id)
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'VoidTransportRequest')
        self.assertEqual(params['ShipmentId'], shipment_id)

    def test_get_package_labels(self):
        """
        GetPackageLabels operation.
        """
        shipment_id = 'E7NBQ1O0Ca'
        num_labels = 53
        page_type = 'PackageLabel_Letter_6'
        params = self.api.get_package_labels(
            shipment_id=shipment_id,
            num_labels=num_labels,
            page_type=page_type,
        )
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'GetPackageLabels')
        self.assertEqual(params['ShipmentId'], shipment_id)
        self.assertEqual(params['PageType'], page_type)
        self.assertEqual(params['NumberOfPackages'], num_labels)

    def test_get_unique_package_labels(self):
        """
        GetUniquePackageLabels operation.
        """
        shipment_id = 'fMSw3SRJkC'
        page_type = 'PackageLabel_Plain_Paper'
        # Case 1: list of package_ids
        package_ids_1 = [
            'BuqFIFFY6d',
            'wU4NmZWEls',
        ]
        params_1 = self.api.get_unique_package_labels(
            shipment_id=shipment_id,
            page_type=page_type,
            package_ids=package_ids_1,
        )
        self.assert_common_params(params_1)
        self.assertEqual(params_1['Action'], 'GetUniquePackageLabels')
        self.assertEqual(params_1['ShipmentId'], shipment_id)
        self.assertEqual(params_1['PageType'], page_type)
        self.assertEqual(params_1['PackageLabelsToPrint.member.1'], package_ids_1[0])
        self.assertEqual(params_1['PackageLabelsToPrint.member.2'], package_ids_1[1])
        # Case 2: single string package_id (should still work)
        package_ids_2 = 'exGsKDTbyb'
        params_2 = self.api.get_unique_package_labels(
            shipment_id=shipment_id,
            page_type=page_type,
            package_ids=package_ids_2,
        )
        self.assert_common_params(params_1)
        self.assertEqual(params_2['Action'], 'GetUniquePackageLabels')
        self.assertEqual(params_2['ShipmentId'], shipment_id)
        self.assertEqual(params_2['PageType'], page_type)
        self.assertEqual(params_2['PackageLabelsToPrint.member.1'], package_ids_2)

    def test_get_pallet_labels(self):
        """
        XYZ operation.
        """
        shipment_id = 'Y3sROqkPfY'
        page_type = 'PackageLabel_A4_4'
        num_labels = 69
        params = self.api.get_pallet_labels(
            shipment_id=shipment_id,
            page_type=page_type,
            num_labels=num_labels,
        )
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'GetPalletLabels')
        self.assertEqual(params['ShipmentId'], shipment_id)
        self.assertEqual(params['PageType'], page_type)
        self.assertEqual(params['NumberOfPallets'], num_labels)

    def test_get_bill_of_lading(self):
        """
        GetBillOfLading operation.
        """
        shipment_id = 'nScOqC6Nh6'
        params = self.api.get_bill_of_lading(
            shipment_id=shipment_id,
        )
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'GetBillOfLading')
        self.assertEqual(params['ShipmentId'], shipment_id)

    def test_list_inbound_shipments(self):
        """
        ListInboundShipments operation.
        """
        shipment_ids = [
            'Fp3kXnLQ72',
            'hAIO0W7VvF',
        ]
        shipment_statuses = [
            'CANCELLED',
            'IN_TRANSIT',
        ]
        last_updated_before = datetime.datetime.utcnow()
        last_updated_after = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        params = self.api.list_inbound_shipments(
            shipment_ids=shipment_ids,
            shipment_statuses=shipment_statuses,
            last_updated_before=last_updated_before,
            last_updated_after=last_updated_after,
        )
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'ListInboundShipments')
        self.assertEqual(params['LastUpdatedBefore'], last_updated_before.isoformat())
        self.assertEqual(params['LastUpdatedAfter'], last_updated_after.isoformat())
        self.assertEqual(params['ShipmentStatusList.member.1'], shipment_statuses[0])
        self.assertEqual(params['ShipmentStatusList.member.2'], shipment_statuses[1])
        self.assertEqual(params['ShipmentIdList.member.1'], shipment_ids[0])
        self.assertEqual(params['ShipmentIdList.member.2'], shipment_ids[1])

    def test_list_inbound_shipments_by_next_token(self):
        """
        ListInboundShipmentsByNextToken operation, via method decorator.
        """
        next_token = 'rK10wZCE03'
        params = self.api.list_inbound_shipments(next_token=next_token)
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'ListInboundShipmentsByNextToken')
        self.assertEqual(params['NextToken'], next_token)

    def test_list_inbound_shipments_by_next_token_alias(self):
        """
        ListInboundShipmentsByNextToken operation, via alias method.
        """
        next_token = 'AscnyUoyhj'
        params = self.api.list_inbound_shipments_by_next_token(next_token)
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'ListInboundShipmentsByNextToken')
        self.assertEqual(params['NextToken'], next_token)

    def test_list_inbound_shipment_items(self):
        """
        ListInboundShipmentItems operation.
        """
        shipment_id = 'P9NLpC2Afi'
        last_updated_before = datetime.datetime.utcnow()
        last_updated_after = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        params = self.api.list_inbound_shipment_items(
            shipment_id=shipment_id,
            last_updated_before=last_updated_before,
            last_updated_after=last_updated_after,
        )
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'ListInboundShipmentItems')
        self.assertEqual(params['ShipmentId'], shipment_id)
        self.assertEqual(params['LastUpdatedBefore'], last_updated_before.isoformat())
        self.assertEqual(params['LastUpdatedAfter'], last_updated_after.isoformat())

    def test_list_inbound_shipment_items_by_next_token(self):
        """
        ListInboundShipmentItemsByNextToken operation, via method decorator.
        """
        next_token = 'kjoslU1R4y'
        params = self.api.list_inbound_shipment_items(next_token=next_token)
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'ListInboundShipmentItemsByNextToken')
        self.assertEqual(params['NextToken'], next_token)

    def test_list_inbound_shipment_items_by_next_token_alias(self):
        """
        ListInboundShipmentItemsByNextToken operation, via alias method.
        """
        next_token = 'p31dr3ceKQ'
        params = self.api.list_inbound_shipment_items_by_next_token(next_token)
        self.assert_common_params(params)
        self.assertEqual(params['Action'], 'ListInboundShipmentItemsByNextToken')
        self.assertEqual(params['NextToken'], next_token)