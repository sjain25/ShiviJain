import time
import bs4
import pandas as pd
import random
import csv
import http.client, urllib.request, urllib.parse, urllib.error, base64
import json

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

normal_delay = random.normalvariate(3, 0.5)
normal_delay_2 = random.normalvariate(5, 0.5)


def reset_driver():
    driver = webdriver.Chrome(executable_path = r'C:\Users\shivi\Downloads\chromedriver_win32\chromedriver.exe')
    driver.get('http://mlb.mlb.com/stats/')
    return driver


def th_text(th):
    return th.abbr.text if th.abbr else th.text


def extract_stats_data(table_html, keep_column_names):
    table_soup = bs4.BeautifulSoup(table_html,'html5lib')
    header_tag = table_soup.thead
    body_tag = table_soup.tbody

    # getting lookup for table names
    lookup = {th['index']: th_text(th).strip() for th in header_tag.findAll('th') if th_text(th) in keep_column_names}

    # getting table with the column name lookup
    data_rows = []
    for row in body_tag.findAll('tr'):
        data_row = {lookup[td['index']]:td.text.replace(u'\xa0',u'') for td  in row if td['index'] in lookup}
        data_rows.append(data_row)

    return pd.DataFrame(data_rows)


def next_page(driver):
    table = driver.find_element_by_id('datagrid')
    table_html = table.get_attribute('innerHTML')
    df = extract_stats_data(table_html, {'Player','AB','Pos'})
    #unable to use while loop with"while True:" condition
    for x in range(0, 11):
        next_button = driver.find_element_by_class_name('paginationWidget-next')
        #-> conceptually wanted to use below condition for paginatio, but it seems it is not working with chrome driver.
        #if "display:none;" in next_button.get_attribute("style"):
        #   break
        next_button.click()
        time.sleep(normal_delay_2)
        page_table = extract_stats_data(table_html, {'Player','AB','Pos'})
        df = df.append(page_table)

    return df


def answer_1():
    driver = reset_driver()
    wait = WebDriverWait(driver, 10)

    stats_team = driver.find_element_by_name('stTab')
    stats_team.click()
    time.sleep(normal_delay)

    hitting_season_element = driver.find_element_by_id('st_hitting_season')
    season_select = Select(hitting_season_element)
    season_select.select_by_value('2015')
    time.sleep(normal_delay)

    hitting_game_element = driver.find_element_by_id('st_hitting_game_type')
    game_select = Select(hitting_game_element)
    game_select.select_by_visible_text('Regular Season')
    time.sleep(normal_delay)

    table = driver.find_element_by_id('datagrid')
    table_html = table.get_attribute('innerHTML')

    df = extract_stats_data(table_html, {'HR','Team'})
    df.to_csv('Question_1.csv')
    test = df.sort_values(['HR'], ascending=[False])
    answer1 = test['Team'].iloc[0]
    print(answer1)


def answer_2a():
    driver = reset_driver()
    wait = WebDriverWait(driver, 10)

    stats_team = driver.find_element_by_name('stTab')
    stats_team.click()
    time.sleep(normal_delay)

    hitting_season_element = driver.find_element_by_id('st_hitting_season')
    season_select = Select(hitting_season_element)
    season_select.select_by_value('2015')
    time.sleep(normal_delay)

    hitting_game_element = driver.find_element_by_id('st_hitting_game_type')
    game_select = Select(hitting_game_element)
    game_select.select_by_visible_text('Regular Season')
    time.sleep(normal_delay)

    hitting_league_element_al = driver.find_element_by_css_selector('#st_hitting-0 > fieldset.widget-radio.ui-buttonset > label:nth-child(4) > span')
    hitting_league_element_al.click()
    time.sleep(normal_delay)

    table = driver.find_element_by_id('datagrid')
    table_html = table.get_attribute('innerHTML')

    df2_al = extract_stats_data(table_html, {'HR','Team'})
    hr_num_al = pd.to_numeric(df2_al["HR"])
    avg_hr_al = hr_num_al.mean()

    hitting_league_element_nl = driver.find_element_by_css_selector('#st_hitting-0 > fieldset.widget-radio.ui-buttonset > label.ui-button.ui-widget.ui-state-default.ui-button-text-only.ui-corner-right > span')
    hitting_league_element_nl.click()
    time.sleep(normal_delay)

    table = driver.find_element_by_id('datagrid')
    table_html = table.get_attribute('innerHTML')

    df2_nl = extract_stats_data(table_html, {'HR','Team'})
    hr_num_nl = pd.to_numeric(df2_nl["HR"])
    avg_hr_nl = hr_num_nl.mean()

    frames = [df2_al,df2_nl]
    df2 = pd.concat(frames)
    df2.to_csv('Question_2a.csv')

    if avg_hr_al > avg_hr_nl:
        print('League name: AL, Average homeruns: ' + str(round(avg_hr_al, 2)))
    else:
        print('League name: NL, Average homeruns: ' + str(round(avg_hr_al, 2)))


def answer_2b():
    driver = reset_driver()
    wait = WebDriverWait(driver, 10)

    stats_team = driver.find_element_by_name('stTab')
    stats_team.click()
    time.sleep(normal_delay)

    hitting_season_element = driver.find_element_by_id('st_hitting_season')
    season_select = Select(hitting_season_element)
    season_select.select_by_value('2015')
    time.sleep(normal_delay)

    hitting_game_element = driver.find_element_by_id('st_hitting_game_type')
    game_select = Select(hitting_game_element)
    game_select.select_by_visible_text('Regular Season')
    time.sleep(normal_delay)

    hitting_split_element = driver.find_element_by_id('st_hitting_hitting_splits')
    split_select = Select(hitting_split_element)
    split_select.select_by_value('i01')
    time.sleep(normal_delay)

    hitting_league_element_al = driver.find_element_by_css_selector('#st_hitting-0 > fieldset.widget-radio.ui-buttonset > label:nth-child(4) > span')
    hitting_league_element_al.click()
    time.sleep(normal_delay)

    table = driver.find_element_by_id('datagrid')
    table_html = table.get_attribute('innerHTML')

    df_fi_al = extract_stats_data(table_html, {'HR','Team'})
    hr_num_al = pd.to_numeric(df_fi_al["HR"])
    avg_hr_fi_al = hr_num_al.mean()

    hitting_league_element_nl = driver.find_element_by_css_selector('#st_hitting-0 > fieldset.widget-radio.ui-buttonset > label.ui-button.ui-widget.ui-state-default.ui-button-text-only.ui-corner-right > span')
    hitting_league_element_nl.click()
    time.sleep(normal_delay)

    table = driver.find_element_by_id('datagrid')
    table_html = table.get_attribute('innerHTML')

    df_fi_nl = extract_stats_data(table_html, {'HR','Team'})
    hr_num_nl = pd.to_numeric(df_fi_nl["HR"])
    avg_hr_fi_nl = hr_num_nl.mean()

    frames = [df_fi_al,df_fi_nl]
    df_fi = pd.concat(frames)
    df_fi.to_csv('Question_2b.csv')

    print('League name: AL, Average homeruns: ' + str(round(avg_hr_fi_al, 2)))
    print('League name: NL, Average homeruns: ' + str(round(avg_hr_fi_nl, 2)))


def answer_3a():
    driver = reset_driver()
    wait = WebDriverWait(driver, 10)

    stats_team = driver.find_element_by_name('stTab')
    stats_team.click()
    time.sleep(normal_delay)

    hitting_season_element = driver.find_element_by_id('st_hitting_season')
    season_select = Select(hitting_season_element)
    season_select.select_by_value('2017')
    time.sleep(normal_delay)

    hitting_game_element = driver.find_element_by_id('st_hitting_game_type')
    game_select = Select(hitting_game_element)
    game_select.select_by_visible_text('Regular Season')
    time.sleep(normal_delay_2)

    team = driver.find_element_by_link_text('New York Yankees')
    team.click()
    time.sleep(normal_delay)

    table = driver.find_element_by_id('datagrid')
    table_html = table.get_attribute('innerHTML')

    avg_batting = extract_stats_data(table_html, {'Player','Pos','AB','AVG'})
    avg_batting.to_csv('Question_3a.csv')
    expression = pd.to_numeric(avg_batting["AB"]) > 30
    ar_above = avg_batting[expression]
    ar_above.sort_values('AVG',ascending=False)
    max_avg_player = ar_above['Player'].iloc[0]
    max_avg_player_pos = ar_above['Pos'].iloc[0]

    team = driver.find_element_by_link_text(max_avg_player)
    team.click()
    time.sleep(normal_delay)

    full_name = driver.find_element_by_css_selector('#roster-search > div > div.pull-right.roster-search-container > div.dropdown.player > span').text

    print("Name: " + full_name)
    print("Position: " + max_avg_player_pos)


def answer_3b():
    driver = reset_driver()
    wait = WebDriverWait(driver, 10)

    stats_team = driver.find_element_by_name('stTab')
    stats_team.click()
    time.sleep(normal_delay)

    hitting_season_element = driver.find_element_by_id('st_hitting_season')
    season_select = Select(hitting_season_element)
    season_select.select_by_value('2017')
    time.sleep(normal_delay)

    hitting_game_element = driver.find_element_by_id('st_hitting_game_type')
    game_select = Select(hitting_game_element)
    game_select.select_by_visible_text('Regular Season')
    time.sleep(normal_delay_2)

    team = driver.find_element_by_link_text('New York Yankees')
    team.click()
    time.sleep(normal_delay)

    table = driver.find_element_by_id('datagrid')
    table_html = table.get_attribute('innerHTML')

    outfield_players = extract_stats_data(table_html, {'Player','Pos','AVG'})
    outfield_players.to_csv('Question_3b.csv')
    outfield_list = ['CL','RF','LF']
    expression = outfield_players['Pos'].isin(outfield_list)
    outfield = outfield_players[expression]
    outfield.sort_values('AVG',ascending=False)
    max_avg_player_outfield = outfield['Player'].iloc[0]
    max_avg_player_outfield_pos = outfield['Pos'].iloc[0]

    team = driver.find_element_by_link_text(max_avg_player_outfield)
    team.click()
    time.sleep(normal_delay)

    full_name = driver.find_element_by_css_selector('#player-header > div > div > h1 > span.player-name').text

    print("Name: " + full_name)
    print("Position: " + max_avg_player_outfield_pos)


def answer_4():
    driver = reset_driver()
    wait = WebDriverWait(driver, 10)

    hitting_season_element = driver.find_element_by_id('sp_hitting_season')
    season_select = Select(hitting_season_element)
    season_select.select_by_value('2015')
    time.sleep(normal_delay)

    hitting_game_element = driver.find_element_by_id('sp_hitting_game_type')
    game_select = Select(hitting_game_element)
    game_select.select_by_visible_text('Regular Season')
    time.sleep(normal_delay)

    player_type = driver.find_element_by_css_selector('#sp_hitting-0 > fieldset:nth-child(5) > label.ui-button.ui-widget.ui-state-default.ui-button-text-only.ui-corner-left > span')
    player_type.click()
    time.sleep(normal_delay)

    hitting_league_element_al = driver.find_element_by_css_selector('#sp_hitting-1 > fieldset.widget-radio.ui-buttonset > label:nth-child(4) > span')
    hitting_league_element_al.click()
    time.sleep(normal_delay)

    all_player_2015 = next_page(driver)
    all_player_2015.to_csv('Question_4.csv')

    ab_num = pd.to_numeric(all_player_2015['AB'],errors='ignore')
    df_alab_2015 = pd.concat([all_player_2015['Player'],ab_num],axis=1)
    sorted_al = df_alab_2015.sort_values('AB',ascending=False)
    player_link = sorted_al['Player'].iloc[0]
    print(player_link)

    while True:
        player = driver.find_elements_by_link_text(player_link)
        time.sleep(normal_delay)
        if not player:
            back_page = driver.find_element_by_css_selector('.paginationWidget-previous')
            back_page.click()
            time.sleep(normal_delay)
            continue
        else:
            player[0].click()
            break

    player_name = driver.find_element_by_css_selector('#player-header > div > div > h1 > span.player-name').text
    player_pos = all_player_2015['Pos'].iloc[0]
    player_team = driver.find_element_by_css_selector('#roster-search > div > div.pull-right.roster-search-container > div.dropdown.team > span').text
    print("Player Name: " + player_name)
    print("Players' position: " + player_pos)
    print("Player Team: " + player_team)


def answer_5():
    driver = reset_driver()
    wait = WebDriverWait(driver, 10)

    hitting_season_element = driver.find_element_by_id('sp_hitting_season')
    season_select = Select(hitting_season_element)
    season_select.select_by_value('2015')
    time.sleep(normal_delay)

    hitting_game_element = driver.find_element_by_id('sp_hitting_game_type')
    game_select = Select(hitting_game_element)
    game_select.select_by_visible_text('All-Star Game')
    time.sleep(normal_delay)

    with open('Latin_America.csv') as file:
        reader = csv.reader(file)
        latin = list(reader)
        latin_countries = [c for country in latin for c in country]

    table = driver.find_element_by_id('datagrid')
    table_html = table.get_attribute('innerHTML')

    all_star_players = extract_stats_data(table_html, {'Player'})
    list_of_players = all_star_players['Player'].tolist()

    la_player_name = []
    la_player_team = []

    for player in list_of_players:
        player_name = driver.find_element_by_link_text(player)
        player_name.click()
        time.sleep(normal_delay_2)
        player_bio = driver.find_elements_by_css_selector('#quick-stats > div.player-bio')
        for word in player_bio:
            if any(country in word.text for country in latin_countries):
                la_player_name.append(driver.find_element_by_css_selector('#player-header > div > div > h1 > span.player-name').text)
                la_player_team.append(driver.find_element_by_css_selector('#roster-search > div > div.pull-right.roster-search-container > div.dropdown.team > span').text)
                driver.back()
                time.sleep(normal_delay_2)
            else:
                driver.back()
                time.sleep(normal_delay)

    la_player_details = pd.DataFrame({'Player Name' : la_player_name, 'Full Team Name': la_player_team})
    la_player_details.to_csv('Question_5.csv')
    print(la_player_details)


def answer_6():
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': '35721dbbb2324520a3e4cbf1e7e16fa8',
    }

    params = urllib.parse.urlencode({})

    # MLB -> Scores -> Schedules -> Season-2016 => DateTime,HomeTeam,AwayTeam,HomeTeamID,AwayTeamID,StadiumID
    try:
        conn = http.client.HTTPSConnection('api.fantasydata.net')
        conn.request("GET", "/v3/mlb/stats/JSON/Games/2016?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data_schedule = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    # taking a JSON string and converting it back to a dictionary structure:
    games = json.loads(data_schedule)

    # MLB -> Scores -> AllTeams => TeamID,Key,Name,StadiumID
    try:
        conn = http.client.HTTPSConnection('api.fantasydata.net')
        conn.request("GET", "/v3/mlb/stats/JSON/AllTeams?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data_allteams = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    allteams = json.loads(data_allteams)

    # MLB -> Scores -> Stadiums -> StadiumID,Name,City,State
    try:
        conn = http.client.HTTPSConnection('api.fantasydata.net')
        conn.request("GET", "/v3/mlb/stats/JSON/Stadiums?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data_stadiums = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    stadiums = json.loads(data_stadiums)

    opponent_team = []
    game_date = []
    stadium_name = []
    city = []
    state = []
    stadium_id = []
    opponent_teamname = []

    for game in games:
        if game['HomeTeam'] == 'HOU':
            game_date.append(game['DateTime'])
            opponent_team.append(game['AwayTeamID'])
            stadium_id.append(game['StadiumID'])
        elif game['AwayTeam'] == 'HOU':
            game_date.append(game['DateTime'])
            opponent_team.append(game['HomeTeamID'])
            stadium_id.append(game['StadiumID'])

    for teamid in opponent_team:
        for team in allteams:
            if teamid == team['TeamID']:
                opponent_teamname.append(team['Name'])

    for id in stadium_id:
        for stadium in stadiums:
            if id == stadium['StadiumID']:
                stadium_name.append(stadium['Name'])
                city.append(stadium['City'])
                state.append(stadium['State'])

    schedule = {'Opponent Team Name':opponent_teamname, 'Date':game_date, 'Stadium Name':stadium_name, 'City':city, 'State':state}
    game_schedule = pd.DataFrame(schedule)
    print(game_schedule)
    game_schedule.to_csv('Question_6.csv')