# -*- coding: utf-8 -*-

from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.transaction import atomic

from _private import populate_permission_matrix

from etools.applications.partners.models import PartnerOrganization
from etools.applications.publics.models import (AirlineCompany, BusinessArea, BusinessRegion, Country,
                                                Currency, DSARegion, Fund, Grant, TravelExpenseType, WBS,)
from etools.applications.users.models import Country as UserCountry, Office


# DEVELOPMENT CODE -
class Command(BaseCommand):
    """
    Usage:
    manage.py et2f_init [--with_users, --with_partners, --with_offices] <username> <password>

    Username and password required to create a user for testing and look up the proper schema.

    -u | --with_users : Import sample users
    -o | --with_offices : Import sample offices
    -p | --with_partners : Import sample partners
    """

    def add_arguments(self, parser):
        parser.add_argument('username', nargs=1)
        parser.add_argument('password', nargs=1, default='password')
        parser.add_argument('-u', '--with_users', action='store_true', default=False)
        parser.add_argument('-o', '--with_offices', action='store_true', default=False)
        parser.add_argument('-p', '--with_partners', action='store_true', default=False)

    @atomic
    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        user = self._get_or_create_admin_user(username, password)
        country = user.profile.country
        connection.set_tenant(country)

        if options.get('with_users'):
            self._load_users()

        self._load_airlines()

        if options.get('with_offices'):
            self._load_offices()

        if options.get('with_partners'):
            self._load_partners()

        self._load_business_areas()
        self._load_currencies()
        self._load_countries()

        self._load_dsa_regions(country)
        self._load_permission_matrix()
        self._add_wbs()
        self._add_grants()
        self._add_funds()
        self._add_expense_types()
        self._add_user_groups()

    def _load_business_areas(self):
        self.stdout.write('Loading business areas')
        business_areas = (
            ('0090', 'Albania', '66', 'CEE_CIS'),
            ('0260', 'Armenia', '66', 'CEE_CIS'),
            ('0310', 'Azerbaijan', '66', 'CEE_CIS'),
            ('0630', 'Belarus', '66', 'CEE_CIS'),
            ('0530', 'Bosnia and Herzegovina', '66', 'CEE_CIS'),
            ('0570', 'Bulgaria', '66', 'CEE_CIS'),
            ('575R', 'CEE/CIS', '66', 'CEE_CIS'),
            ('1030', 'Croatia', '66', 'CEE_CIS'),
            ('1600', 'Georgia', '66', 'CEE_CIS'),
            ('2390', 'Kazakhstan', '66', 'CEE_CIS'),
            ('8971', 'Kosovo', '66', 'CEE_CIS'),
            ('2660', 'Macedonia', '66', 'CEE_CIS'),
            ('5640', 'Moldova', '66', 'CEE_CIS'),
            ('4630', 'Rep of Uzbekistan', '66', 'CEE_CIS'),
            ('4360', 'Rep. of Turkmenistan', '66', 'CEE_CIS'),
            ('2450', 'Republic of Kyrgyzstan', '66', 'CEE_CIS'),
            ('8950', 'Republic of Montenegro', '66', 'CEE_CIS'),
            ('3660', 'Romania', '66', 'CEE_CIS'),
            ('3700', 'Russia', '66', 'CEE_CIS'),
            ('8970', 'Serbia', '66', 'CEE_CIS'),
            ('4150', 'Tajikistan', '66', 'CEE_CIS'),
            ('4350', 'Turkey', '66', 'CEE_CIS'),
            ('4410', 'Ukraine', '66', 'CEE_CIS'),
            ('0660', 'Cambodia', '60', 'EAPR'),
            ('0860', 'China', '60', 'EAPR'),
            ('5150', 'DP Republic of Korea', '60', 'EAPR'),
            ('420R', 'EAPRO, Thailand', '60', 'EAPR'),
            ('1430', 'Fiji (Pacific Islands)', '60', 'EAPR'),
            ('2070', 'Indonesia', '60', 'EAPR'),
            ('2460', 'Lao People\'s Dem Rep.', '60', 'EAPR'),
            ('2700', 'Malaysia', '60', 'EAPR'),
            ('2880', 'Mongolia', '60', 'EAPR'),
            ('0600', 'Myanmar', '60', 'EAPR'),
            ('6490', 'Papua New Guinea', '60', 'EAPR'),
            ('3420', 'Philippines', '60', 'EAPR'),
            ('4200', 'Thailand', '60', 'EAPR'),
            ('7060', 'Timor-Leste', '60', 'EAPR'),
            ('5200', 'Vietnam', '60', 'EAPR'),
            ('6810', 'Angola', '63', 'ESAR'),
            ('0520', 'Botswana', '63', 'ESAR'),
            ('0610', 'Burundi', '63', 'ESAR'),
            ('6620', 'Comoros', '63', 'ESAR'),
            ('1420', 'Eritrea', '63', 'ESAR'),
            ('240R', 'ESARO, Kenya', '63', 'ESAR'),
            ('1410', 'Ethiopia', '63', 'ESAR'),
            ('2400', 'Kenya', '63', 'ESAR'),
            ('2520', 'Lesotho', '63', 'ESAR'),
            ('2670', 'Madagascar', '63', 'ESAR'),
            ('2690', 'Malawi', '63', 'ESAR'),
            ('6980', 'Namibia', '63', 'ESAR'),
            ('6890', 'Republic of Mozambique', '63', 'ESAR'),
            ('3750', 'Rwanda', '63', 'ESAR'),
            ('3920', 'Somalia', '63', 'ESAR'),
            ('3930', 'South Africa', '63', 'ESAR'),
            ('4040', 'South Sudan', '63', 'ESAR'),
            ('4030', 'Swaziland', '63', 'ESAR'),
            ('4380', 'Uganda', '63', 'ESAR'),
            ('4550', 'United Rep. of Tanzania', '63', 'ESAR'),
            ('4980', 'Zambia', '63', 'ESAR'),
            ('6260', 'Zimbabwe', '63', 'ESAR'),
            ('456C', 'Data, Research and Policy', '65', 'HQ'),
            ('1200', 'Denmark', '65', 'HQ'),
            ('456J', 'Div. of Finance & Admin Mgmt', '65', 'HQ'),
            ('456G', 'Division of Communication', '65', 'HQ'),
            ('456K', 'Division of Human Resources', '65', 'HQ'),
            ('456O', 'Evaluation Office', '65', 'HQ'),
            ('456B', 'Executive Director\'s Office', '65', 'HQ'),
            ('456R', 'Field Results Group Office', '65', 'HQ'),
            ('456P', 'Field Sup & Coordination Off', '65', 'HQ'),
            ('575C', 'Geneva Common Services', '65', 'HQ'),
            ('1950', 'Global Shared Service Center', '65', 'HQ'),
            ('456H', 'Gov. & Multilateral Affairs', '65', 'HQ'),
            ('456Q', 'GSSC Project', '65', 'HQ'),
            ('456L', 'InfoTech Solutions & Services', '65', 'HQ'),
            ('456N', 'Int. Audit & Invest (OIAI)', '65', 'HQ'),
            ('456F', 'Office of Emergency Prog.', '65', 'HQ'),
            ('240B', 'Office of Global Innovation', '65', 'HQ'),
            ('2220', 'Office of Research, Italy', '65', 'HQ'),
            ('456S', 'OSEB', '65', 'HQ'),
            ('120X', 'Procurement Services', '65', 'HQ'),
            ('456D', 'Programme Division', '65', 'HQ'),
            ('456I', 'Public Partnerships Division', '65', 'HQ'),
            ('456E', 'Research Division', '65', 'HQ'),
            ('5750', 'Switzerland', '65', 'HQ'),
            ('456T', 'UNICEF Hosted Funds', '65', 'HQ'),
            ('0240', 'Argentina', '62', 'LACR'),
            ('0420', 'Barbados', '62', 'LACR'),
            ('6110', 'Belize', '62', 'LACR'),
            ('0510', 'Bolivia', '62', 'LACR'),
            ('0540', 'Brazil', '62', 'LACR'),
            ('0840', 'Chile', '62', 'LACR'),
            ('0930', 'Colombia', '62', 'LACR'),
            ('1020', 'Costa Rica', '62', 'LACR'),
            ('1050', 'Cuba', '62', 'LACR'),
            ('1260', 'Dominican Republic', '62', 'LACR'),
            ('1350', 'Ecuador', '62', 'LACR'),
            ('1380', 'El Salvador', '62', 'LACR'),
            ('1680', 'Guatemala', '62', 'LACR'),
            ('1800', 'Guyana', '62', 'LACR'),
            ('1830', 'Haiti', '62', 'LACR'),
            ('1860', 'Honduras', '62', 'LACR'),
            ('2280', 'Jamaica', '62', 'LACR'),
            ('333R', 'LACRO, Panama', '62', 'LACR'),
            ('2850', 'Mexico', '62', 'LACR'),
            ('3120', 'Nicaragua', '62', 'LACR'),
            ('3330', 'Panama', '62', 'LACR'),
            ('3360', 'Paraguay', '62', 'LACR'),
            ('3390', 'Peru', '62', 'LACR'),
            ('4620', 'Uruguay', '62', 'LACR'),
            ('4710', 'Venezuela', '62', 'LACR'),
            ('0120', 'Algeria', '59', 'MENA'),
            ('6690', 'Djibouti', '59', 'MENA'),
            ('4500', 'Egypt', '59', 'MENA'),
            ('2100', 'Iran', '59', 'MENA'),
            ('2130', 'Iraq', '59', 'MENA'),
            ('2340', 'Jordan', '59', 'MENA'),
            ('2490', 'Lebanon', '59', 'MENA'),
            ('2580', 'Libya', '59', 'MENA'),
            ('234R', 'MENA, Jordan', '59', 'MENA'),
            ('2910', 'Morocco', '59', 'MENA'),
            ('6350', 'Oman', '59', 'MENA'),
            ('7050', 'Palestine, State of', '59', 'MENA'),
            ('3780', 'Saudi Arabia', '59', 'MENA'),
            ('4020', 'Sudan', '59', 'MENA'),
            ('4140', 'Syria', '59', 'MENA'),
            ('4320', 'Tunisia', '59', 'MENA'),
            ('4920', 'Yemen', '59', 'MENA'),
            ('0060', 'Afghanistan', '64', 'ROSA'),
            ('5070', 'Bangladesh', '64', 'ROSA'),
            ('0490', 'Bhutan', '64', 'ROSA'),
            ('2040', 'India', '64', 'ROSA'),
            ('2740', 'Maldives', '64', 'ROSA'),
            ('2970', 'Nepal', '64', 'ROSA'),
            ('3300', 'Pakistan', '64', 'ROSA'),
            ('297R', 'ROSA, Nepal', '64', 'ROSA'),
            ('0780', 'Sri Lanka', '64', 'ROSA'),
            ('1170', 'Benin', '61', 'WCAR'),
            ('4590', 'Burkina Faso', '61', 'WCAR'),
            ('6820', 'Cabo Verde', '61', 'WCAR'),
            ('0750', 'Central African Republic', '61', 'WCAR'),
            ('0810', 'Chad', '61', 'WCAR'),
            ('3380', 'Congo', '61', 'WCAR'),
            ('2250', 'Cote D\'Ivoire', '61', 'WCAR'),
            ('0990', 'Democratic Republic of Congo', '61', 'WCAR'),
            ('1390', 'Equatorial Guinea', '61', 'WCAR'),
            ('1530', 'Gabon', '61', 'WCAR'),
            ('1560', 'Gambia', '61', 'WCAR'),
            ('1620', 'Ghana', '61', 'WCAR'),
            ('1770', 'Guinea', '61', 'WCAR'),
            ('6850', 'Guinea Bissau', '61', 'WCAR'),
            ('2550', 'Liberia', '61', 'WCAR'),
            ('2760', 'Mali', '61', 'WCAR'),
            ('2820', 'Mauritania', '61', 'WCAR'),
            ('3180', 'Niger', '61', 'WCAR'),
            ('3210', 'Nigeria', '61', 'WCAR'),
            ('0690', 'Republic of Cameroon', '61', 'WCAR'),
            ('6830', 'Sao Tome & Principe', '61', 'WCAR'),
            ('3810', 'Senegal', '61', 'WCAR'),
            ('3900', 'Sierra Leone', '61', 'WCAR'),
            ('4230', 'Togo', '61', 'WCAR'),
            ('381R', 'WCARO, Senegal', '61', 'WCAR')
        )
        business_regions = {ba[2]: ba[3] for ba in business_areas}
        for br_code, br_name in business_regions.items():
            business_regions[br_code], _ = BusinessRegion.objects.get_or_create(name=br_name, code=br_code)

        for ba in business_areas:
            _, created = BusinessArea.objects.get_or_create(name=ba[1],
                                                            code=ba[0],
                                                            region=business_regions[ba[2]])
            if created:
                self.stdout.write('Business area created: {}'.format(ba[1]))
            else:
                self.stdout.write('Business area found: {}'.format(ba[1]))

    def _get_or_create_admin_user(self, username, password):
        User = get_user_model()

        try:
            return User.objects.get(username=username)
        except ObjectDoesNotExist:
            pass

        uat_country = UserCountry.objects.get(name='UAT')

        user = User(username=username,
                    first_name='Puli',
                    last_name='Lab',
                    is_superuser=True,
                    is_staff=True)
        user.set_password(password)
        user.save()

        profile = user.profile
        profile.country = profile.country_override = uat_country
        profile.save()

        self.stdout.write('User was successfully created.')
        return user

    def _load_currencies(self):
        data = ['DZD', 'NAD', 'GHS', 'BZD', 'EGP', 'BGN', 'PAB', 'YUM', 'BOB', 'DKK', 'BWP', 'LBP', 'TZS', 'VND', 'AOA',
                'KHR', 'MYR', 'KYD', 'LYD', 'UAH', 'JOD', 'AWG', 'SAR', 'LTL', 'HKD', 'CHF', 'GIP', 'BYR', 'ALL', 'MRO',
                'HRK', 'DJF', 'THB', 'XAF', 'BND', 'VUV', 'UYU', 'NIO', 'LAK', 'NPR', 'SYP', 'MAD', 'MZM', 'PHP', 'ZAR',
                'PYG', 'GBP', 'NGN', 'ZWD', 'CRC', 'AED', 'EEK', 'MWK', 'LKR', 'SKK', 'PKR', 'HUF', 'ROL', 'SZL', 'LSL',
                'MNT', 'AMD', 'UGX', 'JMD', 'GEL', 'SHP', 'AFN', 'MMK', 'KPW', 'CSD', 'TRY', 'BDT', 'CVE', 'HTG', 'SLL',
                'MGA', 'YER', 'LRD', 'XCD', 'NOK', 'MOP', 'SSP', 'INR', 'MXN', 'CZK', 'TJS', 'BTN', 'COP', 'MUR', 'IDR',
                'HNL', 'XPF', 'FJD', 'ETB', 'PEN', 'MKD', 'ILS', 'DOP', 'TMM', 'MDL', 'QAR', 'SEK', 'MVR', 'AUD', 'SRD',
                'CUP', 'BBD', 'KMF', 'KRW', 'GMD', 'VEF', 'GTQ', 'ANG', 'CLP', 'ZMW', 'EUR', 'CDF', 'RWF', 'KZT', 'RUB',
                'ISK', 'TTD', 'OMR', 'BRL', 'SBD', 'PLN', 'KES', 'SVC', 'USD', 'AZM', 'TOP', 'GNF', 'WST', 'IQD', 'ERN',
                'BAM', 'SCR', 'CAD', 'GYD', 'KWD', 'BIF', 'PGK', 'SOS', 'SGD', 'UZS', 'STD', 'IRR', 'CNY', 'XOF', 'TND',
                'NZD', 'LVL', 'BSD', 'KGS', 'ARS', 'BMD', 'RSD', 'BHD', 'JPY', 'SDG']
        # data = [('United States dollar', 'USD'),
        #         ('Euro', 'EUR'),
        #         ('Japanese yen', 'JPY'),
        #         ('Pound sterling', 'GBP'),
        #         ('Australian dollar', 'AUD'),
        #         ('Canadian dollar', 'CAD'),
        #         ('Swiss franc', 'CHF'),
        #         ('Chinese yuan', 'CNY'),
        #         ('Swedish krona', 'SEK'),
        #         ('Mexican peso', 'MXN'),
        #         ('New Zealand dollar', 'NZD'),
        #         ('Singapore dollar', 'SGD'),
        #         ('Hong Kong dollar', 'HKD'),
        #         ('Norwegian krone', 'NOK'),
        #         ('South Korean won', 'KRW'),
        #         ('Turkish lira', 'TRY'),
        #         ('Indian rupee', 'INR'),
        #         ('Russian ruble', 'RUB'),
        #         ('Brazilian real', 'BRL'),
        #         ('South African rand', 'ZAR')]

        for iso_4217 in data:
            name = iso_4217
            c, created = Currency.objects.get_or_create(iso_4217=iso_4217, defaults={'name': name})
            if created:
                self.stdout.write('Currency created: {} ({})'.format(name, iso_4217))
            else:
                self.stdout.write('Currency found: {} ({})'.format(name, iso_4217))

    def _load_countries(self):
        countries = [('Afghanistan', '0060', 'Afghanistan', 'AFG', '006', 'AF', 'AFG', 'AFN', '19.11.1946', '31.12.9999', 'THE ISLAMIC STATE OF AFGHANISTAN'),
                     ('Albania', '0090', 'Albania', 'ALB', '009', 'AL', 'ALB',
                      'ALL', '14.12.1955', '31.12.9999', 'THE REPUBLIC OF ALBANIA'),
                     ('Algeria', '0120', 'Algeria', 'ALG', '012', 'DZ', 'DZA', 'DZD',
                      '08.10.1962', '31.12.9999', 'THE PEOPLE\'S DEMOCRATIC REPUBLIC OF ALGERIA'),
                     ('Argentina', '0240', 'Argentina', 'ARG', '024', 'AR', 'ARG',
                      'ARS', '24.10.1945', '31.12.9999', 'THE ARGENTINE REPUBLIC'),
                     ('Armenia', '0260', 'Armenia', 'ARM', '026', 'AM', 'ARM',
                      'AMD', '02.03.1992', '31.12.9999', 'THE REPUBLIC OF ARMENIA'),
                     ('Azerbaijan', '0310', 'Azerbaijan', 'AZE', '031', 'AZ', 'AZE',
                      'AZM', '02.03.1992', '31.12.9999', 'THE AZERBAIJANI REPUBLIC'),
                     ('Anguilla', '0420', 'Anguilla', 'ANL', '623', 'AI',
                      'AIA', 'XCD', '20.09.1993', '31.12.9999', 'ANGUILLA'),
                     ('Antigua and Barbuda', '0420', 'Antigua and Barbuda', 'ANT', '601',
                      'AG', 'ATG', 'XCD', '11.11.1981', '31.12.9999', 'ANTIGUA AND BARBUDA'),
                     ('Barbados', '0420', 'Barbados', 'BAR', '042', 'BB',
                      'BRB', 'BBD', '09.12.1966', '31.12.9999', 'BARBADOS'),
                     ('Virgin Islands (UK)', '0420', 'British Virgin Islands', 'BVI', '640',
                      'VG', 'VGB', 'USD', '20.09.1993', '31.12.9999', 'VIRGIN ISLANDS (UK)'),
                     ('Dominica', '0420', 'Dominica', 'DMI', '610', 'DM', 'DMA', 'XCD',
                      '18.12.1978', '31.12.9999', 'THE COMMONWEALTH OF DOMINICA'),
                     ('Grenada', '0420', 'Grenada', 'GRN', '616', 'GD',
                      'GRD', 'XCD', '17.09.1974', '31.12.9999', 'GRENADA'),
                     ('Montserrat', '0420', 'Montserrat', 'MOT', '620', 'MS',
                      'MSR', 'XCD', '20.09.1993', '31.12.9999', 'MONTSERRAT'),
                     ('Saint Kitts and Nevis', '0420', 'St. Kitts and Nevis', 'STK', '627',
                      'KN', 'KNA', 'XCD', '23.09.1983', '31.12.9999', 'SAINT KITTS AND NEVIS'),
                     ('Saint Lucia', '0420', 'St. Lucia', 'STL', '629', 'LC',
                      'LCA', 'XCD', '18.09.1979', '31.12.9999', 'SAINT LUCIA'),
                     ('Saint Vincent and the Grenadines', '0420', 'St.Vincent-Grenadines', 'STV', '630',
                      'VC', 'VCT', 'XCD', '16.09.1980', '31.12.9999', 'SAINT VINCENT AND THE GRENADINES'),
                     ('Turks & Caicos', '0420', 'Turks & Caicos Islands', 'TCI', '636', 'TC',
                      'TCA', 'USD', '20.09.1993', '31.12.9999', 'TURKS AND CAICOS ISLAND'),
                     ('Trinidad and Tobago', '0420', 'Trinidad and Tobago', 'TRI', '429', 'TT', 'TTO',
                      'TTD', '18.09.1962', '31.12.9999', 'THE REPUBLIC OF TRINIDAD AND TOBAGO'),
                     ('Bhutan', '0490', 'Bhutan', 'BHU', '049', 'BT', 'BTN',
                      'BTN', '21.09.1971', '31.12.9999', 'THE KINGDOM OF BHUTAN'),
                     ('Bolivia', '0510', 'Bolivia', 'BOL', '051', 'BO', 'BOL', 'BOB',
                      '14.11.1945', '31.12.9999', 'THE PLURINATIONAL STATE OF BOLIVIA'),
                     ('Botswana', '0520', 'Botswana', 'BOT', '052', 'BW', 'BWA',
                      'BWP', '17.10.1966', '31.12.9999', 'THE REPUBLIC OF BOTSWANA'),
                     ('Bosnia and Herzegovina', '0530', 'Bosnia and Herzegovina', 'BIH', '053', 'BA',
                      'BIH', 'BAM', '22.05.1992', '31.12.9999', 'THE REPUBLIC OF BOSNIA AND HERZEGOVINA'),
                     ('Brazil', '0540', 'Brazil', 'BRA', '054', 'BR', 'BRA', 'BRL',
                      '24.10.1945', '31.12.9999', 'THE FEDERATIVE REPUBLIC OF BRAZIL'),
                     ('Bulgaria', '0570', 'Bulgaria', 'BUL', '057', 'BG', 'BGR',
                      'BGN', '14.12.1955', '31.12.9999', 'THE REPUBLIC OF BULGARIA'),
                     ('Myanmar', '0600', 'Myanmar', 'MYA', '060', 'MM', 'MMR', 'MMK',
                      '19.04.1948', '31.12.9999', 'THE REPUBLIC OF THE UNION OF MYANMAR'),
                     ('Burundi', '0610', 'Burundi', 'BDI', '061', 'BI', 'BDI',
                      'BIF', '18.09.1962', '31.12.9999', 'THE REPUBLIC OF BURUNDI'),
                     ('Belarus', '0630', 'Belarus', 'BYE', '063', 'BY', 'BLR',
                      'BYR', '24.10.1945', '31.12.9999', 'THE REPUBLIC OF BELARUS'),
                     ('Cambodia', '0660', 'Cambodia', 'CMB', '066', 'KH',
                      'KHM', 'KHR', '14.12.1955', '31.12.9999', 'CAMBODIA'),
                     ('Cameroon', '0690', 'Cameroon', 'CMR', '069', 'CM', 'CMR',
                      'XAF', '20.09.1960', '31.12.9999', 'THE REPUBLIC OF CAMEROON'),
                     ('Central African Republic', '0750', 'Central African Rep.', 'CAF', '075', 'CF',
                      'CAF', 'XAF', '20.09.1960', '31.12.9999', 'THE CENTRAL AFRICAN REPUBLIC'),
                     ('Sri Lanka', '0780', 'Sri Lanka', 'SRL', '078', 'LK', 'LKA', 'LKR',
                      '14.12.1955', '31.12.9999', 'THE DEMOCRATIC SOCIALIST REPUBLIC OF SRI LANKA'),
                     ('Chad', '0810', 'Chad', 'CHD', '081', 'TD', 'TCD', 'XAF',
                      '20.09.1960', '31.12.9999', 'THE REPUBLIC OF CHAD'),
                     ('Chile', '0840', 'Chile', 'CHI', '084', 'CL', 'CHL', 'CLP',
                      '24.10.1945', '31.12.9999', 'THE REPUBLIC OF CHILE'),
                     ('China', '0860', 'China', 'CPR', '086', 'CN', 'CHN', 'CNY',
                      '24.10.1945', '31.12.9999', 'THE PEOPLE\'S REPUBLIC OF CHINA'),
                     ('Colombia', '0930', 'Colombia', 'COL', '093', 'CO', 'COL',
                      'COP', '05.11.1945', '31.12.9999', 'THE REPUBLIC OF COLOMBIA'),
                     ('Congo, Dem. Rep.', '0990', 'Congo, Dem. Rep.', 'ZAI', '099', 'CD', 'COD',
                      'CDF', '20.09.1960', '31.12.9999', 'THE DEMOCRATIC REPUBLIC OF CONGO'),
                     ('Costa Rica', '1020', 'Costa Rica', 'COS', '102', 'CR', 'CRI',
                      'CRC', '02.11.1945', '31.12.9999', 'THE REPUBLIC OF COSTA RICA'),
                     ('Croatia', '1030', 'Croatia, Republic of', 'CRO', '103', 'HR',
                      'HRV', 'HRK', '22.05.1992', '31.12.9999', 'THE REPUBLIC OF CROATIA'),
                     ('Cuba', '1050', 'Cuba', 'CUB', '105', 'CU', 'CUB', 'CUP',
                      '24.10.1945', '31.12.9999', 'THE REPUBLIC OF CUBA'),
                     ('Benin', '1170', 'Benin', 'BEN', '117', 'BJ', 'BEN', 'XOF',
                      '20.09.1960', '31.12.9999', 'THE REPUBLIC OF BENIN'),
                     ('Denmark', '1200', 'Denmark', 'DEN', '120', 'DK', 'DNK',
                      'DKK', '24.10.1945', '31.12.9999', 'THE KINGDOM OF DENMARK'),
                     ('Dominican Republic', '1260', 'Dominican Republic', 'DOM', '126', 'DO',
                      'DOM', 'DOP', '24.10.1945', '31.12.9999', 'THE DOMINICAN REPUBLIC'),
                     ('Ecuador', '1350', 'Ecuador', 'ECU', '135', 'EC', 'ECU',
                      'USD', '21.12.1945', '31.12.9999', 'THE REPUBLIC OF ECUADOR'),
                     ('El Salvador', '1380', 'El Salvador', 'ELS', '138', 'SV', 'SLV',
                      'SVC', '24.10.1945', '31.12.9999', 'THE REPUBLIC OF EL SALVADOR'),
                     ('Equatorial Guinea', '1390', 'Equatorial Guinea', 'EQG', '139', 'GQ', 'GNQ',
                      'XAF', '12.11.1968', '31.12.9999', 'THE REPUBLIC OF EQUATORIAL GUINEA'),
                     ('Ethiopia', '1410', 'Ethiopia', 'ETH', '141', 'ET',
                      'ETH', 'ETB', '13.11.1945', '31.12.9999', 'ETHIOPIA'),
                     ('Eritrea', '1420', 'Eritrea', 'ERI', '142', 'ER', 'ERI',
                      'ERN', '28.05.1993', '31.12.9999', 'THE STATE OF ERITREA'),
                     ('American Samoa', '1430', 'American Samoa', 'AMS', '696', 'AS',
                      'ASM', 'USD', '20.09.1993', '31.12.9999', 'AMERICAN SAMOA'),
                     ('Cook Islands', '1430', 'Cook Islands', 'CKI', '679', 'CK',
                      'COK', 'NZD', '20.09.1993', '31.12.9999', 'COOK ISLANDS'),
                     ('Fiji', '1430', 'Fiji', 'FIJ', '143', 'FJ', 'FJI', 'FJD',
                      '13.10.1970', '31.12.9999', 'THE REPUBLIC OF FIJI'),
                     ('Kiribati', '1430', 'Kiribati', 'KIR', '617', 'KI',
                      'KIR', 'AUD', '20.09.1993', '31.12.9999', 'KIRIBATI'),
                     ('Marshall Islands', '1430', 'Marshall Islands', 'MAS', '692', 'MH', 'MHL',
                      'USD', '17.09.1991', '31.12.9999', 'THE REPUBLIC OF THE MARSHALL ISLANDS'),
                     ('Micronesia', '1430', 'Micronesia, Fed States Of', 'MIC', '693', 'FM', 'FSM',
                      'USD', '17.09.1991', '31.12.9999', 'THE FEDERATED STATES OF MICRONESIA'),
                     ('Nauru', '1430', 'Nauru', 'NAU', '648', 'NR', 'NRU', 'AUD',
                      '20.09.1993', '31.12.9999', 'THE REPUBLIC OF NAURU'),
                     ('Niue', '1430', 'Niue', 'NIU', '680', 'NU', 'NIU', 'NZD', '20.09.1993', '31.12.9999', 'NIUE'),
                     ('Palau, Republic Of', '1430', 'Palau', 'PAL', '690', 'PW', 'PLW',
                      'USD', '15.12.1994', '31.12.9999', 'THE REPUBLIC OF PALAU'),
                     ('Samoa', '1430', 'Samoa', 'SAM', '590', 'WS', 'WSM', 'WST',
                      '24.10.1945', '31.12.9999', 'THE INDEPENDANT STATE OF WESTERN SAMOA'),
                     ('Solomon Islands', '1430', 'Solomon Islands', 'SOI', '631', 'SB',
                      'SLB', 'SBD', '19.09.1978', '31.12.9999', 'SOLOMON ISLANDS'),
                     ('Tokelau', '1430', 'Tokelau', 'TOK', '656', 'TK', 'TKL',
                      'NZD', '20.09.1993', '31.12.9999', 'TOKELAU ISLANDS'),
                     ('Tonga', '1430', 'Tonga', 'TON', '634', 'TO', 'TON',
                      'TOP', '20.09.1993', '31.12.9999', 'THE KINGDOM OF TONGA'),
                     ('Tuvalu', '1430', 'Tuvalu', 'TUV', '618', 'TV', 'TUV', 'AUD', '20.09.1993', '31.12.9999', 'TUVALU'),
                     ('Vanuatu', '1430', 'Vanuatu', 'VAN', '655', 'VU', 'VUT',
                      'VUV', '15.09.1981', '31.12.9999', 'THE REPUBLIC OF VANUATU'),
                     ('Gabon', '1530', 'Gabon', 'GAB', '153', 'GA', 'GAB', 'XAF',
                      '20.09.1960', '31.12.9999', 'THE GABONESE REPUBLIC'),
                     ('Gambia', '1560', 'Gambia', 'GAM', '156', 'GM', 'GMB', 'GMD',
                      '21.09.1965', '31.12.9999', 'THE REPUBLIC OF THE GAMBIA'),
                     ('Georgia', '1600', 'Georgia, Republic of', 'GEO', '160', 'GE',
                      'GEO', 'GEL', '31.07.1992', '31.12.9999', 'THE REPUBLIC OF GEORGIA'),
                     ('Ghana', '1620', 'Ghana', 'GHA', '162', 'GH', 'GHA', 'GHS',
                      '08.03.1957', '31.12.9999', 'THE REPUBLIC OF GHANA'),
                     ('Guatemala', '1680', 'Guatemala', 'GUA', '168', 'GT', 'GTM',
                      'GTQ', '21.11.1945', '31.12.9999', 'THE REPUBIC OF GUATEMALA'),
                     ('Guinea', '1770', 'Guinea', 'GUI', '177', 'GN', 'GIN',
                      'GNF', '12.12.1958', '31.12.9999', 'THE REPUBLIC OF GUINEA'),
                     ('Guyana', '1800', 'Guyana', 'GUY', '180', 'GY', 'GUY',
                      'GYD', '20.09.1966', '31.12.9999', 'THE REPUBLIC OF GUYANA'),
                     ('Suriname', '1800', 'Suriname', 'SUR', '678', 'SR', 'SUR',
                      'SRD', '04.12.1975', '31.12.9999', 'THE REPUBLIC OF SURINAME'),
                     ('Haiti', '1830', 'Haiti', 'HAI', '183', 'HT', 'HTI', 'HTG',
                      '24.10.1945', '31.12.9999', 'THE REPUBLIC OF HAITI'),
                     ('Honduras', '1860', 'Honduras', 'HON', '186', 'HN', 'HND',
                      'HNL', '17.12.1945', '31.12.9999', 'THE REPUBLIC OF HONDURAS'),
                     ('India', '2040', 'India', 'IND', '204', 'IN', 'IND', 'INR',
                      '30.10.1945', '31.12.9999', 'THE REPUBLIC OF INDIA'),
                     ('Indonesia', '2070', 'Indonesia', 'INS', '207', 'ID', 'IDN',
                      'IDR', '28.09.1950', '31.12.9999', 'THE REPUBLIC OF INDONESIA'),
                     ('Iran', '2100', 'Iran', 'IRA', '210', 'IR', 'IRN', 'IRR',
                      '24.10.1945', '31.12.9999', 'THE ISLAMIC REPUBLIC OF IRAN'),
                     ('Iraq', '2130', 'Iraq', 'IRQ', '213', 'IQ', 'IRQ', 'IQD',
                      '21.12.1945', '31.12.9999', 'THE REPUBLIC OF IRAQ'),
                     ('Cote D\'Ivoire', '2250', 'Cote d Ivoire', 'IVC', '225', 'CI', 'CIV',
                      'XOF', '20.09.1960', '31.12.9999', 'THE REPUBLIC OF COTE D\'IVOIRE'),
                     ('Jamaica', '2280', 'Jamaica', 'JAM', '228', 'JM',
                      'JAM', 'JMD', '18.09.1962', '31.12.9999', 'JAMAICA'),
                     ('Jordan', '2340, 234R', 'Jordan', 'JOR', '234', 'JO', 'JOR', 'JOD',
                      '14.12.1955', '31.12.9999', 'THE HASHEMITE KINGDOM OF JORDAN'),
                     ('Kazakhstan', '2390', 'Kazakhstan', 'KAZ', '239', 'KZ', 'KAZ',
                      'KZT', '02.03.1992', '31.12.9999', 'THE REPUBLIC OF KAZAKHSTAN'),
                     ('Kenya', '2400, 240R', 'Kenya', 'KEN', '240', 'KE', 'KEN',
                      'KES', '16.12.1963', '31.12.9999', 'THE REPUBLIC OF KENYA'),
                     ('Kyrgyzstan', '2450', 'Kyrgyzstan', 'KYR', '245', 'KG',
                      'KGZ', 'KGS', '02.03.1992', '31.12.9999', 'KYRGYSTAN'),
                     ('Lao, People\'s Dem. Rep', '2460', 'Lao Peo. Dem. Rep.', 'LAO', '246', 'LA',
                      'LAO', 'LAK', '14.12.1955', '31.12.9999', 'THE LAO PEOPLE\'S DEMOCRATIC REPUBLIC'),
                     ('Lebanon', '2490', 'Lebanon', 'LEB', '249', 'LB', 'LBN',
                      'LBP', '24.10.1945', '31.12.9999', 'THE LEBANESE REPUBLIC'),
                     ('Lesotho', '2520', 'Lesotho', 'LES', '252', 'LS', 'LSO',
                      'LSL', '17.10.1966', '31.12.9999', 'THE KINGDOM OF LESOTHO'),
                     ('Liberia', '2550', 'Liberia', 'LIR', '255', 'LR', 'LBR',
                      'LRD', '02.11.1945', '31.12.9999', 'THE REPUBLIC OF LIBERIA'),
                     ('Libya', '2580', 'Libya', 'LIB', '258', 'LY', 'LBY', 'LYD', '14.12.1955', '31.12.9999', 'LIBYA'),
                     ('Macedonia, TFYR', '2660', 'The former Yugoslav Republic of Macedonia', 'MCD', '266', 'MK',
                      'MKD', 'MKD', '08.04.1993', '31.12.9999', 'THE FORMER YUGOSLAV REPUBLIC OF MACEDONIA'),
                     ('Madagascar', '2670', 'Madagascar', 'MAG', '267', 'MG', 'MDG', 'MGA',
                      '20.09.1960', '31.12.9999', 'THE DEMOCRATIC REPUBLIC OF MADAGASCAR'),
                     ('Malawi', '2690', 'Malawi', 'MLW', '269', 'MW', 'MWI',
                      'MWK', '01.12.1964', '31.12.9999', 'THE REPUBLIC OF MALAWI'),
                     ('Malaysia', '2700', 'Malaysia', 'MAL', '270', 'MY',
                      'MYS', 'MYR', '17.09.1957', '31.12.9999', 'MALAYSIA'),
                     ('Maldives', '2740', 'Maldives', 'MDV', '274', 'MV', 'MDV',
                      'MVR', '21.09.1965', '31.12.9999', 'THE REPUBLIC OF MALDIVES'),
                     ('Mali', '2760', 'Mali', 'MLI', '276', 'ML', 'MLI', 'XOF',
                      '28.09.1960', '31.12.9999', 'THE REPUBLIC OF MALI'),
                     ('Mauritania', '2820', 'Mauritania', 'MAU', '282', 'MR', 'MRT', 'MRO',
                      '27.10.1961', '31.12.9999', 'THE ISLAMIC REPUBLIC OF MAURITANIA'),
                     ('Mexico', '2850', 'Mexico', 'MEX', '285', 'MX', 'MEX', 'MXN',
                      '07.11.1945', '31.12.9999', 'THE UNITED MEXICAN STATES'),
                     ('Mongolia', '2880', 'Mongolia', 'MON', '288', 'MN',
                      'MNG', 'MNT', '27.10.1961', '31.12.9999', 'MONGOLIA'),
                     ('Morocco', '2910', 'Morocco', 'MOR', '291', 'MA', 'MAR',
                      'MAD', '12.11.1956', '31.12.9999', 'THE KINGDOM OF MOROCCO'),
                     ('Nepal', '2970, 297R', 'Nepal', 'NEP', '297', 'NP', 'NPL', 'NPR',
                      '14.12.1955', '31.12.9999', 'THE FEDERAL DEMOCRATIC REPUBLIC OF NEPAL'),
                     ('Nicaragua', '3120', 'Nicaragua', 'NIC', '312', 'NI', 'NIC',
                      'NIO', '24.10.1945', '31.12.9999', 'THE REPUBLIC OF NICARAGUA'),
                     ('Niger', '3180', 'Niger', 'NER', '318', 'NE', 'NER', 'XOF',
                      '20.09.1960', '31.12.9999', 'THE REPUBLIC OF THE NIGER'),
                     ('Nigeria', '3210', 'Nigeria', 'NIR', '321', 'NG', 'NGA', 'NGN',
                      '07.10.1960', '31.12.9999', 'THE FEDERAL REPUBLIC OF NIGERIA'),
                     ('Pakistan', '3300', 'Pakistan', 'PAK', '330', 'PK', 'PAK', 'PKR',
                      '30.09.1947', '31.12.9999', 'THE ISLAMIC REPUBLIC OF PAKISTAN'),
                     ('Panama', '3330, 333R', 'Panama', 'PAN', '333', 'PA', 'PAN',
                      'PAB', '13.11.1945', '31.12.9999', 'THE REPUBLIC OF PANAMA'),
                     ('Paraguay', '3360', 'Paraguay', 'PAR', '336', 'PY', 'PRY',
                      'PYG', '24.10.1945', '31.12.9999', 'THE REPUBLIC OF PARAGUAY'),
                     ('Congo', '3380', 'Congo', 'PRC', '338', 'CG', 'COG', 'XAF',
                      '20.09.1960', '31.12.9999', 'THE REPUBLIC OF THE CONGO'),
                     ('Peru', '3390', 'Peru', 'PER', '339', 'PE', 'PER', 'PEN',
                      '31.10.1945', '31.12.9999', 'THE REPUBLIC OF PERU'),
                     ('Philippines', '3420', 'Philippines', 'PHI', '342', 'PH', 'PHL',
                      'PHP', '24.10.1945', '31.12.9999', 'THE REPUBLIC OF THE PHILIPPINES'),
                     ('Romania', '3660', 'Romania', 'ROM', '366', 'RO',
                      'ROU', 'ROL', '14.12.1955', '31.12.9999', 'ROMANIA'),
                     ('Russian Federation', '3700', 'Russian Federation', 'RUS', '370', 'RU',
                      'RUS', 'RUB', '24.12.1991', '31.12.9999', 'THE RUSSIAN FEDERATION'),
                     ('Rwanda', '3750', 'Rwanda', 'RWA', '375', 'RW', 'RWA',
                      'RWF', '18.09.1962', '31.12.9999', 'THE RWANDESE REPUBLIC'),
                     ('Bahrain', '3780', 'Bahrain', 'BAH', '604', 'BH', 'BHR',
                      'BHD', '21.09.1971', '31.12.9999', 'THE STATE OF BAHRAIN'),
                     ('Kuwait', '3780', 'Kuwait', 'KUW', '243', 'KW', 'KWT',
                      'KWD', '14.05.1963', '31.12.9999', 'THE STATE OF KUWAIT'),
                     ('Qatar', '3780', 'Qatar', 'QAT', '624', 'QA', 'QAT',
                      'QAR', '21.09.1971', '31.12.9999', 'THE STATE OF QATAR'),
                     ('Saudi Arabia', '3780', 'Saudi Arabia', 'SAU', '378', 'SA', 'SAU',
                      'SAR', '24.10.1945', '31.12.9999', 'THE KINGDOM OF SAUDI ARABIA'),
                     ('United Arab Emirates', '3780', 'United Arab Emirates', 'UAE', '449', 'AE',
                      'ARE', 'AED', '09.12.1971', '31.12.9999', 'UNITED ARAB EMIRATES (THE)'),
                     ('Senegal', '3810, 381R', 'Senegal', 'SEN', '381', 'SN', 'SEN',
                      'XOF', '28.09.1960', '31.12.9999', 'THE REPUBLIC OF SENEGAL'),
                     ('Sierra Leone', '3900', 'Sierra Leone', 'SIL', '390', 'SL', 'SLE',
                      'SLL', '27.09.1961', '31.12.9999', 'THE REPUBLIC OF SIERRA LEONE'),
                     ('Somalia', '3920', 'Somalia', 'SOM', '392', 'SO', 'SOM', 'SOS',
                      '20.09.1960', '31.12.9999', 'THE SOMALI DEMOCRATIC REPUBLIC'),
                     ('South Africa', '3930', 'South Africa', 'SAF', '393', 'ZA', 'ZAF',
                      'ZAR', '07.11.1945', '31.12.9999', 'THE REPUBLIC OF SOUTH AFRICA'),
                     ('Sudan', '4020', 'Sudan', 'SUD', '402', 'SD', 'SDN', 'SDG',
                      '12.11.1956', '31.12.9999', 'THE REPUBLIC OF THE SUDAN'),
                     ('Swaziland', '4030', 'Swaziland', 'SWA', '403', 'SZ', 'SWZ',
                      'SZL', '24.09.1968', '31.12.9999', 'THE KINGDOM OF SWAZILAND'),
                     ('South Sudan', '4040', 'South Sudan, Republic of', 'SSD', '404',
                      'SS', 'SSD', 'SSP', '14.07.2011', '31.12.9999', 'SOUTH SUDAN'),
                     ('Syrian Arab Republic', '4140', 'Syrian Arab Republic', 'SYR', '414', 'SY',
                      'SYR', 'SYP', '24.10.1945', '31.12.9999', 'SYRIAN ARAB REPUBLIC (THE)'),
                     ('Tajikistan', '4150', 'Tajikistan', 'TAJ', '415', 'TJ', 'TJK',
                      'TJS', '02.03.1992', '31.12.9999', 'THE REPUBLIC OF TAJIKISTAN'),
                     ('Thailand', '4200, 420R', 'Thailand', 'THA', '420', 'TH', 'THA',
                      'THB', '16.12.1946', '31.12.9999', 'THE KINGDOM OF THAILAND'),
                     ('Togo', '4230', 'Togo', 'TOG', '423', 'TG', 'TGO', 'XOF',
                      '20.09.1960', '31.12.9999', 'THE TOGOLESE REPUBLIC'),
                     ('Tunisia', '4320', 'Tunisia', 'TUN', '432', 'TN', 'TUN',
                      'TND', '12.11.1956', '31.12.9999', 'THE REPUBLIC OF TUNISIA'),
                     ('Turkey', '4350', 'Turkey', 'TUR', '435', 'TR', 'TUR',
                      'TRY', '24.10.1945', '31.12.9999', 'THE REPUBLIC OF TURKEY'),
                     ('Turkmenistan', '4360', 'Turkmenistan', 'TUK', '436', 'TM',
                      'TKM', 'TMM', '02.03.1992', '31.12.9999', 'TURKMENISTAN'),
                     ('Uganda', '4380', 'Uganda', 'UGA', '438', 'UG', 'UGA',
                      'UGX', '25.10.1962', '31.12.9999', 'THE REPUBLIC OF UGANDA'),
                     ('Ukraine', '4410', 'Ukraine', 'UKR', '441', 'UA',
                      'UKR', 'UAH', '24.10.1945', '31.12.9999', 'UKRAINE'),
                     ('Egypt', '4500', 'Egypt', 'EGY', '450', 'EG', 'EGY', 'EGP',
                      '24.10.1945', '31.12.9999', 'THE ARAB REPUBLIC OF EGYPT'),
                     ('Tanzania, United Rep. of', '4550', 'Tanzania, United Rep. of', 'URT', '455', 'TZ',
                      'TZA', 'TZS', '14.12.1961', '31.12.9999', 'UNITED REPUBLIC OF TANZANIA (THE)'),
                     ('Burkina Faso', '4590', 'Burkina Faso', 'BKF', '459', 'BF',
                      'BFA', 'XOF', '20.09.1960', '31.12.9999', 'BURKINA FASO'),
                     ('Uruguay', '4620', 'Uruguay', 'URU', '462', 'UY', 'URY', 'UYU',
                      '18.12.1945', '31.12.9999', 'THE EASTERN REPUBLIC OF URUGUAY'),
                     ('Uzbekistan', '4630', 'Uzbekistan', 'UZB', '463', 'UZ', 'UZB',
                      'UZS', '02.03.1992', '31.12.9999', 'THE REPUBLIC OF UZBEKISTAN'),
                     ('Venezuela', '4710', 'Venezuela', 'VEN', '471', 'VE', 'VEN', 'VEF',
                      '15.11.1945', '31.12.9999', 'VENEZUELA, BOLIVARIAN REPUBLIC OF'),
                     ('Yemen', '4920', 'Yemen, Republic of', 'YEM', '492', 'YE', 'YEM',
                      'YER', '30.09.1947', '31.12.9999', 'THE REPUBLIC OF YEMEN'),
                     ('Zambia', '4980', 'Zambia', 'ZAM', '498', 'ZM', 'ZMB',
                      'ZMW', '01.12.1964', '31.12.9999', 'THE REPUBLIC OF ZAMBIA'),
                     ('Bangladesh', '5070', 'Bangladesh', 'BGD', '507', 'BD', 'BGD', 'BDT',
                      '17.09.1974', '31.12.9999', 'THE PEOPLE\'S REPUBLIC OF BANGLADESH'),
                     ('Korea, Democratic People\'s Republic of', '5150', 'Korea, Dem. Peo. of', 'DRK', '515', 'KP',
                      'PRK', 'KPW', '17.09.1991', '31.12.9999', 'THE DEMOCRATIC PEOPLE\'S REPUBLIC OF KOREA'),
                     ('Viet Nam', '5200', 'Vietnam', 'VIE', '520', 'VN', 'VNM', 'VND',
                      '20.09.1977', '31.12.9999', 'THE SOCIALIST REPUBLIC OF VIET NAM'),
                     ('Moldova', '5640', 'Moldova', 'MOL', '564', 'MD', 'MDA',
                      'MDL', '02.03.1992', '31.12.9999', 'THE REPUBLIC OF MOLDOVA'),
                     ('Switzerland', '575R', 'Switzerland', 'SWI', '575', 'CH', 'CHE',
                      'CHF', '20.09.1993', '31.12.9999', 'THE SWISS CONFEDERATION'),
                     ('Belize', '6110', 'Belize', 'BZE', '611', 'BZ', 'BLZ', 'BZD', '25.09.1981', '31.12.9999', 'BELIZE'),
                     ('Zimbabwe', '6260', 'Zimbabwe', 'ZIM', '626', 'ZW', 'ZWE',
                      'ZWD', '25.08.1980', '31.12.9999', 'THE REPUBLIC OF ZIMBABWE'),
                     ('Oman', '6350', 'Oman', 'OMA', '635', 'OM', 'OMN', 'OMR',
                      '07.10.1971', '31.12.9999', 'THE SULTANATE OF OMAN'),
                     ('Papua New Guinea', '6490', 'Papua New Guinea', 'PNG', '649', 'PG',
                      'PNG', 'PGK', '10.10.1975', '31.12.9999', 'PAPUA NEW GUINEA'),
                     ('Comoros', '6620', 'Comoros', 'COI', '662', 'KM', 'COM', 'KMF',
                      '12.11.1975', '31.12.9999', 'THE ISLAMIC FEDERAL REPUBLIC OF THE COMOROS'),
                     ('Djibouti', '6690', 'Djibouti', 'DJI', '669', 'DJ', 'DJI',
                      'DJF', '20.09.1977', '31.12.9999', 'THE REPUBLIC OF DJIBOUTI'),
                     ('Angola', '6810', 'Angola', 'ANG', '681', 'AO', 'AGO',
                      'AOA', '01.12.1976', '31.12.9999', 'THE REPUBLIC OF ANGOLA'),
                     ('Cabo Verde', '6820', 'Cape Verde', 'CVI', '682', 'CV', 'CPV',
                      'CVE', '16.09.1975', '31.12.9999', 'REPUBLIC OF CABO VERDE'),
                     ('Sao Tome and Principe', '6830', 'Sao Tome and Principe', 'STP', '683', 'ST', 'STP',
                      'STD', '16.09.1975', '31.12.9999', 'THE DEMOCRATIC REPUBLIC OF SAO TOME AND PRINCIPE'),
                     ('Guinea-Bissau', '6850', 'Guinea Bissau', 'GBS', '685', 'GW', 'GNB',
                      'XOF', '17.09.1974', '31.12.9999', 'THE REPUBLIC OF GUINEA-BISSAU'),
                     ('Mozambique', '6890', 'Mozambique', 'MOZ', '689', 'MZ', 'MOZ',
                      'MZM', '16.09.1975', '31.12.9999', 'THE REPUBLIC OF MOZAMBIQUE'),
                     ('Namibia', '6980', 'Namibia', 'NAM', '698', 'NA', 'NAM',
                      'NAD', '23.04.1990', '31.12.9999', 'THE REPUBLIC OF NAMIBIA'),
                     ('Palestine', '7050', 'West Bank', 'OCT', '705', 'PS', 'PSE',
                      'ILS', '03.03.1993', '31.12.9999', 'PALESTINE, STATE OF'),
                     ('Timor-Leste', '7060', 'Timor-Leste', 'TIM', '706', 'TL',
                      'TLS', 'USD', '25.10.1999', '31.12.9999', 'TIMOR-LESTE'),
                     ('Montenegro', '8950', 'Montenegro', 'MNE', '895', 'ME', 'MNE',
                      'EUR', '28.06.2006', '31.12.9999', 'REPUBLIC OF MONTENEGRO'),
                     ('Serbia', '8970, 8971', 'Serbia', 'SRB', '897', 'RS', 'SRB',
                      'RSD', '04.02.2003', '31.12.9999', 'REPUBLIC OF SERBIA'),
                     ('Aruba', '', 'Aruba', 'ARU', '025', 'AW', 'ABW', 'AWG', '20.09.1993', '31.12.9999', 'ARUBA'),
                     ('Australia', '', 'Australia', 'AUL', '027', 'AU',
                      'AUS', 'AUD', '01.11.1945', '31.12.9999', 'AUSTRALIA'),
                     ('Austria', '', 'Austria', 'AUS', '030', 'AT', 'AUT', 'EUR',
                      '14.12.1955', '31.12.9999', 'THE REPUBLIC OF AUSTRIA'),
                     ('Belgium', '', 'Belgium', 'BEL', '048', 'BE', 'BEL', 'EUR',
                      '27.12.1945', '31.12.9999', 'THE KINGDOM OF BELGIUM'),
                     ('Bermuda', '', 'Bermuda', 'BER', '605', 'BM', 'BMU', 'BMD', '20.09.1993', '31.12.9999', 'BERMUDA'),
                     ('Bahamas', '', 'Bahamas', 'BHA', '603', 'BS', 'BHS', 'BSD',
                      '18.09.1973', '31.12.9999', 'THE COMMONWEALTH OF THE BAHAMAS'),
                     ('Brunei', '', 'Brunei', 'BRU', '602', 'BN', 'BRN',
                      'BND', '21.09.1984', '31.12.9999', 'BRUNEI DARUSSALAM'),
                     ('Canary Islands', '', 'Canary Islands', 'CAI', '071', '',
                      '', 'EUR', '01.04.1996', '31.12.9999', 'CANARY ISLANDS'),
                     ('Canada', '', 'Canada', 'CAN', '072', 'CA', 'CAN', 'CAD', '09.11.1945', '31.12.9999', 'CANADA'),
                     ('Cayman Islands', '', 'Cayman Islands', 'CAY', '615', 'KY',
                      'CYM', 'KYD', '20.09.1993', '31.12.9999', 'CAYMAN ISLANDS'),
                     ('Czech Republic', '', 'Czech Republic', 'CEH', '113', 'CZ',
                      'CZE', 'CZK', '19.01.1993', '31.12.9999', 'THE CZECH REPUBLIC'),
                     ('Curacao', '', 'Curacao', 'CUW', '', '', '', '', '', '', ''),
                     ('Cyprus', '', 'Cyprus', 'CYP', '111', 'CY', 'CYP', 'EUR',
                      '20.09.1960', '31.12.9999', 'THE REPUBLIC OF CYPRUS'),
                     ('Estonia', '', 'Estonia', 'EST', '140', 'EE', 'EST', 'EEK',
                      '17.09.1991', '31.12.9999', 'THE REPUBLIC OF ESTONIA'),
                     ('Finland', '', 'Finland', 'FIN', '144', 'FI', 'FIN', 'EUR',
                      '14.12.1955', '31.12.9999', 'THE REPUBLIC OF FINLAND'),
                     ('France', '', 'France', 'FRA', '147', 'FR', 'FRA', 'EUR',
                      '24.10.1945', '31.12.9999', 'THE FRENCH REPUBLIC'),
                     ('Germany', '', 'Germany', 'GER', '525', 'DE', 'DEU', 'EUR',
                      '03.10.1990', '31.12.9999', 'THE FEDERAL REPUBLIC OF GERMANY'),
                     ('Gibraltar', '', 'Gibraltar', 'GIB', '163', 'GI',
                      'GIB', 'GIP', '01.04.1996', '31.12.9999', 'GIBRALTER'),
                     ('Greece', '', 'Greece', 'GRE', '165', 'GR', 'GRC', 'EUR',
                      '25.10.1945', '31.12.9999', 'THE HELLENIC REPUBLIC'),
                     ('Guam', '', 'Guam', 'GUM', '004', 'GU', 'GUM', 'USD', '01.04.1996', '31.12.9999', 'GUAM'),
                     ('Hong Kong', '', 'China, Hong Kong', 'HOK', '612', 'HK',
                      'HKG', 'HKD', '20.09.1993', '31.12.9999', 'HONG KONG'),
                     ('Hungary', '', 'Hungary', 'HUN', '195', 'HU', 'HUN', 'HUF', '14.12.1955', '31.12.9999', 'HUNGARY'),
                     ('Iceland', '', 'Iceland', 'ICE', '198', 'IS', 'ISL', 'ISK',
                      '19.11.1946', '31.12.9999', 'THE REPUBLIC OF ICELAND'),
                     ('Ireland', '', 'Ireland', 'IRE', '216', 'IE', 'IRL', 'EUR', '14.12.1955', '31.12.9999', 'IRELAND'),
                     ('Israel', '', 'Israel', 'ISR', '219', 'IL', 'ISR', 'ILS',
                      '11.05.1949', '31.12.9999', 'THE STATE OF ISRAEL'),
                     ('Italy', '', 'Italy', 'ITA', '222', 'IT', 'ITA', 'EUR',
                      '14.12.1955', '31.12.9999', 'THE ITALIAN REPUBLIC'),
                     ('Japan', '', 'Japan', 'JPN', '231', 'JP', 'JPN', 'JPY', '18.12.1956', '31.12.9999', 'JAPAN'),
                     ('Latvia', '', 'Latvia', 'LAT', '247', 'LV', 'LVA', 'LVL',
                      '17.09.1991', '31.12.9999', 'THE REPUBLIC OF LATVIA'),
                     ('Lithuania', '', 'Lithuania', 'LIT', '260', 'LT', 'LTU', 'LTL',
                      '17.09.1991', '31.12.9999', 'THE REPUBLIC OF LITHUANIA'),
                     ('Luxembourg', '', 'Luxembourg', 'LUX', '264', 'LU', 'LUX', 'EUR',
                      '24.10.1945', '31.12.9999', 'THE GRAND DUCHY OF LUXEMBOURG'),
                     ('Macau', '', 'China, Macau', 'MAC', '688', 'MO', 'MAC', 'MOP', '01.01.1993', '31.12.9999', 'MACAU'),
                     ('Mauritius', '', 'Mauritius', 'MAR', '283', 'MU',
                      'MUS', 'MUR', '24.04.1968', '31.12.9999', 'MAURITIUS'),
                     ('Malta', '', 'Malta', 'MAT', '279', 'MT', 'MLT', 'EUR',
                      '01.12.1964', '31.12.9999', 'THE REPUBLIC OF MALTA'),
                     ('Monaco', '', 'Monaco', 'MNC', '565', 'MC', 'MCO', 'EUR',
                      '28.05.1993', '31.12.9999', 'THE PRINCIPALITY OF MONACO'),
                     ('New Caledonia', '', 'New Caledonia', 'NCA', '667', 'NC',
                      'NCL', 'XPF', '20.09.1993', '31.12.9999', 'NEW CALEDONIA'),
                     ('Netherlands', '', 'Netherlands', 'NET', '300', 'NL', 'NLD', 'EUR',
                      '10.12.1945', '31.12.9999', 'THE KINGDOM OF THE NETHERLANDS'),
                     ('Norway', '', 'Norway', 'NOR', '324', 'NO', 'NOR', 'NOK',
                      '27.11.1945', '31.12.9999', 'THE KINGDOM OF NORWAY'),
                     ('New Zealand', '', 'New Zealand', 'NZE', '309', 'NZ',
                      'NZL', 'NZD', '24.10.1945', '31.12.9999', 'NEW ZEALAND'),
                     ('Poland', '', 'Poland', 'POL', '345', 'PL', 'POL', 'PLN',
                      '24.10.1945', '31.12.9999', 'THE REPUBLIC OF POLAND'),
                     ('Portugal', '', 'Portugal', 'POR', '348', 'PT', 'PRT', 'EUR',
                      '14.12.1955', '31.12.9999', 'THE PORTUGUESE REPUBLIC'),
                     ('Puerto Rico', '', 'Puerto Rico', 'PUE', '695', 'PR',
                      'PRI', 'USD', '20.09.1993', '31.12.9999', 'PUERTO RICO'),
                     ('Korea, Republic of', '', 'Korea, Republic of', 'ROK', '567', 'KR',
                      'KOR', 'KRW', '17.09.1991', '31.12.9999', 'REPUBLIC OF KOREA (THE)'),
                     ('Western Sahara', '', 'Western Sahara', 'SAH', '691', 'EH',
                      'ESH', 'MAD', '20.09.1993', '31.12.9999', 'WESTERN SAHARA'),
                     ('Seychelles', '', 'Seychelles', 'SEY', '628', 'SC', 'SYC',
                      'SCR', '21.09.1976', '31.12.9999', 'THE REPUBLIC OF SEYCHELLES'),
                     ('Singapore', '', 'Singapore', 'SIN', '391', 'SG', 'SGP', 'SGD',
                      '21.09.1965', '31.12.9999', 'THE REPUBLIC OF SINGAPORE'),
                     ('Slovakia', '', 'Slovak Republic', 'SLO', '395', 'SK', 'SVK',
                      'SKK', '19.01.1993', '31.12.9999', 'THE REPUBLIC OF SLOVAKIA'),
                     ('Spain', '', 'Spain', 'SPA', '399', 'ES', 'ESP', 'EUR',
                      '14.12.1955', '31.12.9999', 'THE KINGDOM OF SPAIN'),
                     ('Slovenia', '', 'Slovenia, Republic of', 'SVN', '394', 'SI', 'SVN',
                      'EUR', '22.05.1992', '31.12.9999', 'THE REPUBLIC OF SLOVENIA'),
                     ('Sweden', '', 'Sweden', 'SWE', '411', 'SE', 'SWE', 'SEK',
                      '19.11.1946', '31.12.9999', 'THE KINGDOM OF SWEDEN'),
                     ('Saint Maarten', '', 'Saint Maarten', 'SXM', '', '', '', '', '', '', ''),
                     ('United Kingdom', '', 'United Kingdom', 'U.K', '453', 'GB', 'GBR', 'GBP',
                      '24.10.1945', '31.12.9999', 'THE UNITED KINGDOM OF GREAT BRITAIN AND NORTHERN I'),
                     ('United States of America', '', 'USA', 'USA', '456', 'US', 'USA',
                      'USD', '24.10.1945', '31.12.9999', 'UNITED STATES OF AMERICA (THE)'),
                     ('Virgin Islands (USA)', '', 'Virgin Islands', 'UVI', '697', 'VI', 'VIR',
                      'USD', '20.09.1993', '31.12.9999', 'VIRGIN ISLANDS OF THE UNITED STATES'),
                     ('Andorra', '', 'Andorra', '', '505', 'AD', 'AND', 'EUR',
                      '28.07.1993', '31.12.9999', 'THE PRINCIPALITY OF ANDORRA'),
                     ('French Antilles', '', 'French Antilles', '', '660', '',
                      '', 'XCD', '20.09.1993', '31.12.9999', 'FRENCH ANTILLES'),
                     ('French Guiana', '', 'French Guiana', '', '665', 'GF',
                      'GUF', 'EUR', '20.09.1993', '31.12.9999', 'FRENCH GUIANA'),
                     ('French Polynesia (France)', '', 'French Polynesia (France)', '', '668',
                      'PF', 'PYF', 'XPF', '20.09.1993', '31.12.9999', 'FRENCH POLYNESIA'),
                     ('Greenland', '', 'Greenland', '', '001', 'GL', 'GRL', 'DKK', '01.04.1996', '31.12.9999', 'GREENLAND'),
                     ('Guadeloupe', '', 'Guadeloupe', '', '666', 'GP', 'GLP',
                      'EUR', '20.09.1993', '31.12.9999', 'GUADELOUPE'),
                     ('Liechtenstein', '', 'Liechtenstein', '', '555', 'LI', 'LIE', 'CHF',
                      '18.09.1990', '31.12.9999', 'THE PRINCIPALITY OF LIECHTENSTEIN'),
                     ('Martinique', '', 'Martinique', '', '664', 'MQ', 'MTQ',
                      'EUR', '01.01.1993', '31.12.9999', 'MARTINIQUE'),
                     ('Netherlands Antilles', '', 'Netherlands Antilles', '', '672', 'AN',
                      'ANT', 'ANG', '20.09.1993', '31.12.9999', 'NETHERLANDS ANTILLES'),
                     ('Northern Mariana Islands', '', 'Northern Mariana Islands', '', '700',
                      'MP', 'MNP', 'USD', '01.04.1996', '31.12.9999', 'NORTHERN MARIANA ISLANDS'),
                     ('Not Applicable', '', 'Not Applicable', '', '701', 'OT',
                      '', '', '24.10.1945', '31.12.9999', 'NOT APPLICABLE'),
                     ('Reunion', '', 'Reunion', '', '663', 'RE', 'REU', 'EUR', '20.09.1993', '31.12.9999', 'REUNION'),
                     ('Saint Helena', '', 'Saint Helena', '', '625', 'SH',
                      'SHN', 'SHP', '20.09.1993', '31.12.9999', 'SAINT HELENA'),
                     ('San Marino', '', 'San Marino', '', '570', 'SM', 'SMR', 'EUR',
                      '02.03.1992', '31.12.9999', 'THE REPUBLIC OF SAN MARINO'),
                     ('Serbia & Montenegro', '', 'Serbia & Montenegro', '', '891', 'CS',
                      'SRB', 'CSD', '02.04.2003', '31.12.9999', 'SERBIA AND MONTENEGRO'),
                     ('Sikkim', '', 'Sikkim', '', '645', '', '', '', '20.09.1993', '31.12.9999', 'SIKKIM'),
                     ('Stateless', '', 'Stateless', '', '499', '', '', '', '24.10.1945', '31.12.9999', 'STATELESS'),
                     ('United Nations', '', 'United Nations', '', '999', 'UN',
                      '', 'USD', '01.01.1998', '31.12.9999', 'UNITED NATIONS'),
                     ('Unknown', '', 'Unknown', '', '000', 'UU', '', '', '', '31.12.9999', ''),
                     ('Vatican City', '', 'Vatican City', '', '535', 'VA', 'VAT',
                      'EUR', '20.09.1993', '31.12.9999', 'HOLY SEE (THE)'),
                     ('Wallis & Futuna Islands', '', 'Wallis & Futuna Islands', '', '661', 'WF',
                      'WLF', 'XPF', '20.09.1993', '31.12.9999', 'WALLIS & FUTUNA ISLANDS'),
                     ('Yugoslavia', '', 'Yugoslavia', '', '495', 'YU', '', 'YUM', '24.10.1945', '31.12.9999', 'THE FEDERAL REPUBLIC OF YUGOSLAVIA')]

        for name, ba_code, _, _, vision_code, iso_2, iso_3, currency_code, valid_from, valid_to, long_name in countries:
            if valid_from:
                valid_from = datetime.strptime(valid_from, '%d.%m.%Y')
            else:
                valid_from = None

            if valid_to:
                valid_to = datetime.strptime(valid_to, '%d.%m.%Y')
            else:
                valid_to = None

            c, created = Country.objects.get_or_create(name=name,
                                                       long_name=long_name,
                                                       vision_code=vision_code,
                                                       business_area=BusinessArea.objects.filter(code=ba_code).first(),
                                                       iso_2=iso_2,
                                                       iso_3=iso_3,
                                                       currency=Currency.objects.filter(
                                                           iso_4217=currency_code).first(),
                                                       valid_from=valid_from,
                                                       valid_to=valid_to)
            if created:
                self.stdout.write('Country created: {}'.format(name))
            else:
                self.stdout.write('Country found: {}'.format(name))

    def _load_users(self):
        User = get_user_model()
        user_full_names = ['Kathryn Cruz', 'Jonathan Wright', 'Timothy Kelly', 'Brenda Nguyen', 'Matthew Morales',
                           'Timothy Watson', 'Jacqueline Brooks', 'Steve Olson', 'Lawrence Patterson', 'Lois Jones',
                           'Margaret White', 'Clarence Stanley', 'Bruce Williamson', 'Susan Carroll', 'Philip Wood',
                           'Emily Jenkins', 'Christina Robinson', 'Jason Young', 'Joyce Freeman', 'Jack Murphy',
                           'Katherine Garcia', 'Sean Perkins', 'Howard Peterson', 'Denise Coleman', 'Benjamin Evans',
                           'Carl Watkins', 'Martin Morris', 'Nicole Stephens', 'Thomas Willis', 'Ann Ferguson',
                           'Russell Hanson', 'Janet Johnston', 'Adam Bowman', 'Elizabeth Mendoza', 'Helen Robertson',
                           'Wanda Fowler', 'Roger Richardson', 'Bobby Carroll', 'Donna Sims', 'Shawn Peters',
                           'Lisa Davis', 'Laura Riley', 'Jason Freeman', 'Ashley Hill', 'Joseph Gonzales',
                           'Brenda Dixon', 'Paul Wilson', 'Tammy Reyes', 'Beverly Bishop', 'James Weaver',
                           'Samuel Vasquez', 'Albert Baker', 'Keith Wright', 'Michael Hart', 'Shirley Allen',
                           'Samuel Gutierrez', 'Cynthia Riley', 'Roy Simpson', 'Raymond Wagner', 'Eric Taylor',
                           'Steven Bell', 'Jane Powell', 'Paula Morales', 'James Hamilton', 'Shirley Perez',
                           'Maria Olson', 'Amy Dunn', 'Frances Bowman', 'Billy Lawrence', 'Beverly Howell', 'Amy Sims',
                           'Carlos Sanchez', 'Nicholas Harvey', 'Walter Wheeler', 'Bruce Morales', 'Kathy Reynolds',
                           'Lisa Lopez', 'Ann Medina', 'Raymond Washington', 'Jessica Brown', 'Harold Stone',
                           'Paul Hill', 'Wayne Foster', 'Brian Garza', 'Craig Sims', 'Adam Morales', 'Brandon Miller',
                           'Dennis Green', 'Linda Banks', 'Sandra Dunn', 'Randy Rogers', 'Jimmy West', 'Julia Grant',
                           'Judy Ryan', 'William Carroll', 'Mary Rose', 'Ann Nelson', 'Rebecca Hill', 'Robert Rivera',
                           'Rebecca Weaver']

        for full_name in user_full_names:
            first_name, last_name = full_name.split()
            username = full_name.replace(' ', '_').lower()
            u, created = User.objects.get_or_create(username=username, defaults={'first_name': first_name,
                                                                                 'last_name': last_name})
            if created:
                self.stdout.write('User created: {} ({})'.format(full_name, username))
            else:
                self.stdout.write('User found: {} ({})'.format(full_name, username))

    def _load_airlines(self):
        airlines = [('American Airlines', 'AA', 1, 'AAL', 'United States'),
                    ('Blue Panorama', 'BV', 4, 'BPA', 'Italy'),
                    ('Adria Airways', 'JP', 165, 'ADR', 'Slovenia'),
                    ('Aegean Airlines', 'A3', 390, 'AEE', 'Greece'),
                    ('Aerolineas Argentinas', 'AR', 44, 'ARG', 'Argentina'),
                    ('Aeromexico', 'AM', 139, 'AMX', 'Mexico'),
                    ('Air Algérie', 'AH', 124, 'DAH', 'Algeria'),
                    ('Air Berlin', 'AB', 745, 'BER', 'Germany'),
                    ('Air Burkina', '2J', 226, 'VBW', 'Burkina Faso'),
                    ('Air Caledonie', 'TY', 190, 'TPC', 'New Caledonia'),
                    ('Air Canada', 'AC', 14, 'ACA', 'Canada'),
                    ('Air Europa', 'UX', 996, 'AEA', 'Spain'),
                    ('Air France', 'AF', 57, 'AFR', 'France'),
                    ('Air India ', 'AI', 98, 'AIC', 'India'),
                    ('Air Koryo', 'JS', 120, 'KOR', 'Korea, Democratic People\'s Republic of'),
                    ('Air Madagascar', 'MD', 258, 'MDG', 'Madagascar'),
                    ('Air Mauritius', 'MK', 239, 'MAU', 'Mauritius'),
                    ('Air SERBIA a.d. Beograd', 'JU', 115, 'ASL', 'Serbia'),
                    ('Air Seychelles', 'HM', 61, 'SEY', 'Seychelles'),
                    ('Aircalin', 'SB', 63, 'ACI', 'New Caledonia'),
                    ('Alaska Airlines', 'AS', 27, 'ASA', 'United States'),
                    ('Alitalia', 'AZ', 55, 'AZA', 'Italy'),
                    ('All Nippon Airways', 'NH', 205, 'ANA', 'Japan'),
                    ('AlMasria Universal Airlines', 'UJ', 110, 'LMU', 'Egypt'),
                    ('Arik Air', 'W3', 725, 'ARA', 'Nigeria'),
                    ('Arkia Israeli Airlines ', 'IZ', 238, 'AIZ', 'Israel'),
                    ('Asiana', 'OZ', 988, 'AAR', 'Korea'),
                    ('AVIANCA', 'AV', 134, 'AVA', 'Colombia'),
                    ('Azul Brazilian Airlines', 'AD', 577, 'AZU', 'Brazil'),
                    ('Bangkok Air ', 'PG', 829, 'BKP', 'Thailand'),
                    ('British Airways', 'BA', 125, 'BAW', 'United Kingdom'),
                    ('Brussels Airlines', 'SN', 82, 'BEL', 'Belgium'),
                    ('Camair-Co', 'QC', 40, '0', 'Cameroon'),
                    ('Cargolux S.A.', 'CV', 172, 'CLX', 'Luxembourg'),
                    ('Caribbean Airlines', 'BW', 106, 'BWA', 'Trinidad and Tobago'),
                    ('Carpatair', 'V3', 21, 'KRP', 'Romania'),
                    ('Cathay Dragon', 'KA', 43, 'HDA', 'Hong Kong SAR, China'),
                    ('Cathay Pacific', 'CX', 160, 'CPA', 'Hong Kong SAR, China'),
                    ('China Eastern', 'MU', 781, 'CES', 'China (People\'s Republic of)'),
                    ('China Southern Airlines', 'CZ', 784, 'CSN', 'China (People\'s Republic of)'),
                    ('Comair', 'MN', 161, 'CAW', 'South Africa'),
                    ('Czech Airlines j.s.c', 'OK', 64, 'CSA', 'Czech Republic'),
                    ('Delta Air Lines', 'DL', 6, 'DAL', 'United States'),
                    ('DHL Aviation EEMEA B.S.C.(c) ', 'ES*', 155, 'DHX', 'Bahrain'),
                    ('Dniproavia', 'Z6*', 181, 'UDN', 'Ukraine'),
                    ('Egyptair', 'MS', 77, 'MSR', 'Egypt'),
                    ('EL AL', 'LY', 114, 'ELY', 'Israel'),
                    ('Emirates', 'EK', 176, 'UAE', 'United Arab Emirates'),
                    ('Ethiopian Airlines', 'ET', 71, 'ETH', 'Ethiopia'),
                    ('Etihad Airways', 'EY', 607, 'ETD', 'United Arab Emirates'),
                    ('Eurowings', 'EW', 104, 'EWG', 'Germany'),
                    ('Fiji Airways', 'FJ', 260, 'FJI', 'Fiji'),
                    ('Finnair', 'AY', 105, 'FIN', 'Finland'),
                    ('flybe', 'BE', 267, 'BEE', 'United Kingdom'),
                    ('flydubai', 'FZ', 141, 'FDB', 'United Arab Emirates'),
                    ('Garuda', 'GA', 126, 'GIA', 'Indonesia'),
                    ('Germania', 'ST', 246, 'GMI', 'Germany'),
                    ('Hahn Air', 'HR*', 169, 'HHN', 'Germany'),
                    ('Hawaiian Airlines', 'HA', 173, 'HAL', 'United States'),
                    ('IBERIA', 'IB', 75, 'IBE', 'Spain'),
                    ('Icelandair', 'FI', 108, 'ICE', 'Iceland'),
                    ('Iran Air', 'IR', 96, 'IRA', 'Iran, Islamic Republic of'),
                    ('Japan Airlines', 'JL', 131, 'JAL', 'Japan'),
                    ('Jet Airways', '9W', 589, 'JAI', 'India'),
                    ('JetBlue', 'B6', 279, 'JBU', 'United States'),
                    ('Kenya Airways', 'KQ', 706, 'KQA', 'Kenya'),
                    ('KLM', 'KL', 74, 'KLM', 'Netherlands'),
                    ('Korean Air', 'KE', 180, 'KAL', 'Korea'),
                    ('Kuwait Airways', 'KU', 229, 'KAC', 'Kuwait'),
                    ('LACSA', 'LR', 133, 'LRC', 'Costa Rica'),
                    ('LAM', 'TM', 68, 'LAM', 'Mozambique'),
                    ('Lao Airlines', 'QV', 627, 'LAO', 'Lao People\'s Democratic Republic'),
                    ('LATAM Airlines Brasil', 'JJ', 957, 'TAM', 'Brazil'),
                    ('LATAM Airlines Colombia', '4C', 35, 'ARE', 'Colombia'),
                    ('LATAM Airlines Group', 'LA', 45, 'LAN', 'Chile'),
                    ('LATAM Cargo Chile', 'UC', 145, 'LCO', 'Chile'),
                    ('LOT Polish Airlines', 'LO', 80, 'LOT', 'Poland'),
                    ('Lufthansa', 'LH', 220, 'DLH', 'Germany'),
                    ('Malaysia Airlines', 'MH', 232, 'MAS', 'Malaysia'),
                    ('MEA', 'ME', 76, 'MEA', 'Lebanon'),
                    ('Olympic Air', 'OA', 50, 'OAL', 'Greece'),
                    ('Oman Air', 'WY', 910, 'OAS', 'Oman'),
                    ('Pegasus Airlines', 'PC', 624, 'PGT', 'Turkey'),
                    ('Philippine Airlines', 'PR', 79, 'PAL', 'Philippines'),
                    ('PIA', 'PK', 214, 'PIA', 'Pakistan'),
                    ('Qatar Airways', 'QR', 157, 'QTR', 'Qatar'),
                    ('Rossiya Airlines ', 'FV', 195, 'SDM', 'Russian Federation'),
                    ('Royal Air Maroc', 'AT', 147, 'RAM', 'Morocco'),
                    ('Royal Jordanian', 'RJ', 512, 'RJA', 'Jordan'),
                    ('SAA', 'SA', 83, 'SAA', 'South Africa'),
                    ('SAS', 'SK', 117, 'SAS', 'Sweden'),
                    ('Saudi Arabian Airlines', 'SV', 65, 'SVA', 'Saudi Arabia'),
                    ('Shanghai Airlines', 'FM', 774, '0', 'China (People\'s Republic of)'),
                    ('Sichuan Airlines ', '3U', 876, '0', 'China (People\'s Republic of)'),
                    ('SriLankan', 'UL', 603, 'ALK', 'Sri Lanka'),
                    ('SWISS', 'LX', 724, 'SWR', 'Switzerland'),
                    ('Syrianair', 'RB', 70, 'SYR', 'Syrian Arab Republic'),
                    ('TAME - Linea Aérea del Ecuador', 'EQ', 269, 'TAE', 'Ecuador'),
                    ('TAP Portugal', 'TP', 47, 'TAP', 'Portugal'),
                    ('TAROM ', 'RO', 281, 'ROT', 'Romania'),
                    ('Thai Airways International', 'TG', 217, 'THA', 'Thailand'),
                    ('THY - Turkish Airlines', 'TK', 235, 'THY', 'Turkey'),
                    ('Ukraine International Airlines', 'PS', 566, 'AUI', 'Ukraine'),
                    ('United Airlines', 'UA', 16, 'UAL', 'United States'),
                    ('UTair', 'UT', 298, 'UTA', 'Russian Federation'),
                    ('Uzbekistan Airways', 'HY', 250, 'UZB', 'Uzbekistan'),
                    ('Vietnam Airlines', 'VN', 738, 'HVN', 'Vietnam'),
                    ('Virgin Atlantic', 'VS', 932, 'VIR', 'United Kingdom'),
                    ('Virgin Australia', 'VA', 795, 'VAU', 'Australia'),
                    ('VRG Linhas Aéreas S.A. - Grupo GOL', 'G3', 127, 'GLO', 'Brazil'),
                    ('WestJet', 'WS', 838, 'WJA', 'Canada'),
                    ('White coloured by you', 'WI', 97, 'WHT', 'Portugal')]

        AirlineCompany.objects.all().delete()

        for airline_name, iata, code, icao, country in airlines:
            a, created = AirlineCompany.objects.get_or_create(name=airline_name, defaults={'iata': iata,
                                                                                           'code': code,
                                                                                           'icao': icao,
                                                                                           'country': country})
            if created:
                self.stdout.write('Airline created: {}'.format(airline_name))
            else:
                self.stdout.write('Airline found: {}'.format(airline_name))

    def _load_offices(self):
        offices = ('Pulilab', 'Unicef HQ')

        for office_name in offices:
            o, created = Office.objects.get_or_create(name=office_name)
            if created:
                o.offices.add(connection.tenant)
                self.stdout.write('Office created: {}'.format(office_name))
            else:
                self.stdout.write('Office found: {}'.format(office_name))

    def _load_partners(self):
        partners = ['Dynazzy', 'Yodoo', 'Omba', 'Eazzy', 'Avamba', 'Jaxworks', 'Thoughtmix', 'Bubbletube', 'Mydo',
                    'Photolist', 'Gevee', 'Buzzdog', 'Quinu', 'Edgewire', 'Yambee', 'Ntag', 'Muxo',
                    'Edgetag', 'Tagfeed', 'BlogXS', 'Feedbug', 'Babblestorm', 'Skimia', 'Linkbridge', 'Fatz', 'Kwimbee',
                    'Yodo', 'Skibox', 'Zoomzone', 'Meemm', 'Twitterlist', 'Kwilith', 'Skipfire', 'Wikivu', 'Topicblab',
                    'BlogXS', 'Brightbean', 'Skimia', 'Mycat', 'Tagcat', 'Meedoo', 'Vitz', 'Realblab', 'Babbleopia',
                    'Pixonyx', 'Dabshots', 'Gabcube', 'Yoveo', 'Realblab', 'Tagcat']

        for partner_name in partners:
            p, created = PartnerOrganization.objects.get_or_create(name=partner_name)
            if created:
                self.stdout.write('Partner created: {}'.format(partner_name))
            else:
                self.stdout.write('Partner found: {}'.format(partner_name))

    def _load_dsa_regions(self, country):
        dsa_region_data = [{'dsa_amount_usd': 300,
                            'country': Country.objects.filter(name='Hungary').last(),
                            'room_rate': 120,
                            'dsa_amount_60plus_usd': 200,
                            'dsa_amount_60plus_local': 56000,
                            'dsa_amount_local': 84000,
                            'finalization_date': datetime.now().date(),
                            'eff_date': datetime.now().date(),
                            'area_name': 'Everywhere',
                            'area_code': country.business_area_code},
                           {'dsa_amount_usd': 400,
                            'country': Country.objects.filter(name='Germany').last(),
                            'room_rate': 150,
                            'dsa_amount_60plus_usd': 260,
                            'dsa_amount_60plus_local': 238.68,
                            'dsa_amount_local': 367.21,
                            'finalization_date': datetime.now().date(),
                            'eff_date': datetime.now().date(),
                            'area_name': 'Everywhere',
                            'area_code': country.business_area_code}]
        for data in dsa_region_data:
            name = data.pop('country')
            d, created = DSARegion.objects.get_or_create(country=name, defaults=data)
            if created:
                self.stdout.write('DSA Region created: {}'.format(name))
            else:
                self.stdout.write('DSA Region found: {}'.format(name))

    def _load_permission_matrix(self):
        populate_permission_matrix(self)

    def _add_wbs(self):
        wbs_data_list = [
            {'name': 'WBS #1'},
            {'name': 'WBS #2'},
            {'name': 'WBS #3'},
        ]

        for data in wbs_data_list:
            name = data.pop('name')
            r, created = WBS.objects.get_or_create(name=name)
            if created:
                self.stdout.write('WBS created: {}'.format(name))
            else:
                self.stdout.write('WBS found: {}'.format(name))

    def _add_grants(self):
        wbs_1 = WBS.objects.get(name='WBS #1')
        wbs_2 = WBS.objects.get(name='WBS #2')
        wbs_3 = WBS.objects.get(name='WBS #3')

        grant_data_list = [
            {'name': 'Grant #1',
             'wbs': wbs_1},
            {'name': 'Grant #2',
             'wbs': wbs_1},
            {'name': 'Grant #3',
             'wbs': wbs_2},
            {'name': 'Grant #4',
             'wbs': wbs_2},
            {'name': 'Grant #5',
             'wbs': wbs_3}
        ]

        for data in grant_data_list:
            name = data.pop('name')
            g, created = Grant.objects.get_or_create(name=name, defaults=data)
            if created:
                self.stdout.write('Grant created: {}'.format(name))
            else:
                self.stdout.write('Grant found: {}'.format(name))

    def _add_funds(self):
        grant_1 = Grant.objects.get(name='Grant #1')
        grant_2 = Grant.objects.get(name='Grant #2')
        grant_3 = Grant.objects.get(name='Grant #3')
        grant_4 = Grant.objects.get(name='Grant #4')
        grant_5 = Grant.objects.get(name='Grant #5')

        fund_data_list = [
            {'name': 'Fund #1',
             'grant': grant_1},
            {'name': 'Fund #2',
             'grant': grant_1},
            {'name': 'Fund #3',
             'grant': grant_2},
            {'name': 'Fund #4',
             'grant': grant_3},
            {'name': 'Fund #5',
             'grant': grant_3},
            {'name': 'Fund #6',
             'grant': grant_4},
            {'name': 'Fund #7',
             'grant': grant_4},
            {'name': 'Fund #8',
             'grant': grant_5},
            {'name': 'Fund #4',
             'grant': grant_5},
            {'name': 'Fund #4',
             'grant': grant_5},
        ]

        for data in fund_data_list:
            name = data.pop('name')
            f, created = Fund.objects.get_or_create(name=name, defaults=data)
            if created:
                self.stdout.write('Fund created: {}'.format(name))
            else:
                self.stdout.write('Fund found: {}'.format(name))

    def _add_expense_types(self):
        expense_type_data = [
            {'title': 'Food',
             'code': 'food'},
            {'title': 'Tickets',
             'code': 'tickets'},
            {'title': 'Fees',
             'code': 'fees'}
        ]

        for data in expense_type_data:
            title = data.pop('title')
            e, created = TravelExpenseType.objects.get_or_create(title=title, defaults=data)
            if created:
                self.stdout.write('Expense type created: {}'.format(title))
            else:
                self.stdout.write('Expense type found: {}'.format(title))

    def _add_user_groups(self):
        group_names = ['Representative Office',
                       'Finance Focal Point',
                       'Travel Focal Point',
                       'Travel Administrator']
        for name in group_names:
            g, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write('Group created: {}'.format(name))
            else:
                self.stdout.write('Group found: {}'.format(name))

# DEVELOPMENT CODE - END