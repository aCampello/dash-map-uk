import pandas as pd
from pycountry_convert import country_name_to_country_alpha3
from pycountry_convert import country_alpha3_to_country_alpha2
from pycountry_convert import country_alpha2_to_country_name
from pycountry_convert import map_countries
from argparse import ArgumentParser


def country_to_code(country):
    """
    Convert a country name to a code name (alpha3), taking into account errors
    
    :param country: 
    :return: code alpha3
    """
    countries = map_countries().keys()

    try:
        code = country_name_to_country_alpha3(country)
    except KeyError:
        # If there is no exact match try sub-strings
        for country_name in countries:
            if country_name in country:
                code = country_name_to_country_alpha3(country_name)
                break
            elif country in country_name:
                code = country_name_to_country_alpha3(country_name)
                break
        else:
            code = country

    return code

def get_visa_data(year_of_interest):
    entry_visas = pd.read_csv('data/entry-visas-work.csv')

    year_of_interest = str(year_of_interest)

    entry_visas = entry_visas[entry_visas['Quarter'].apply(lambda year: year[:4]) == year_of_interest]
    entry_visas['Total'] = entry_visas['Total'].apply(lambda number: ('0' if ('z' in number) else number))
    entry_visas['Total'] = entry_visas['Total'].apply(lambda number: number.replace(',', ''))
    entry_visas['Total'] = pd.to_numeric(entry_visas['Total'])

    # Manually converts some of the country names to standard (for some reason they are out of standards)

    conversion_of_country_names = {'Korea (North)': 'North Korea', 'Korea (South)': 'South Korea',
                                   'Occupied Palestinian Territories': 'the State of Palestine',
                                   'Virgin Islands (British)': 'British Virgin Islands',
                                   'Virgin Islands (US)': 'United States Virgin Islands',
                                   'Burma': 'Myanmar'}

    entry_visas.Country.replace(to_replace=conversion_of_country_names, inplace=True)

    entry_visas['country_code'] = entry_visas['Country'].apply(country_to_code)

    # Separate refugees and deletes very small entries
    entry_visas_refugees = entry_visas[entry_visas['country_code'] == 'Refugees']

    df = entry_visas[entry_visas['country_code'].apply(len) <= 3]
    grouped = df.groupby(by='Country').sum()
    grouped.reset_index(inplace=True)
    grouped['country_code'] = grouped['Country'].apply(country_to_code)

    # Creates dictionary of geographical regions
    dictionary_of_regions = {item['Country']: item['Geographical region'] for [_, item] in df.iterrows()}
    grouped['Geographical region'] = grouped['Country'].replace(dictionary_of_regions)

    countries = map_countries().keys()
    list_of_country_codes = list(set([country_to_code(country) for country in countries]))

    # Fills the country codes that do not show up in the table with zeros

    grouped.set_index('country_code', inplace=True)

    for code in list_of_country_codes:
        if code not in grouped.index:
            country_name = country_alpha2_to_country_name(country_alpha3_to_country_alpha2(code))
            grouped.loc[code] = [country_name, 0, 'Other']

    grouped.reset_index(inplace=True)

    filename = 'map_of_immigration_' + year_of_interest + '.csv'
    grouped.to_csv('data/'+filename)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-y', '--year', dest='year')

    args = parser.parse_args()

    if args.year:
        get_visa_data(year_of_interest=args.year)
    else:
        print('Parsing all years from 2005...')

        for year in range(2005, 2018):
            print(year, end=' ')
            get_visa_data(year_of_interest=year)

