#!/usr/bin/env python
#
# Based on ticker scripts from the Homemade Sports Ticker
# https://medium.com/@mikemetral/a-homemade-sports-ticker-875c73a5339
#
#===============================================================================
import pytz
import datetime
import time
import urllib2
import json
import xml.etree.ElementTree as ET

#-------------------------------------------------------------------------------
URL = "http://scores.nbcsports.msnbc.com" + \
        "/ticker/data/gamesMSNBC.js.asp?jsonp=true&sport=%s&period=%d"
#-------------------------------------------------------------------------------
# Golf Scores get pulled and formatted differently...

def golf(league):
	SportsInfoURL = "http://scores.nbcsports.msnbc.com/ticker/data/sports.js.asp?jsonp=true&sport=%s&period=%d"
	leaguename = 'Golf'
	
	yyyymmdd = int(datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%Y%m%d"))

	date = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%D")
	sports = []
	max_attempts = 1

	for attempt in range(max_attempts):
		try:
			f = urllib2.urlopen(SportsInfoURL % (leaguename, yyyymmdd))
			jsonp = f.read()
			f.close()
			json_str = jsonp.replace('shsMSNBCTicker.loadSportsData(', '').replace(');', '')
			json_parsed = json.loads(json_str)
             	
			#for sport_str in json_parsed.get('sport',[]):
			for sport_str in json_parsed:
					sport = sport_str.get('sport').strip("#1234567890 ")
					if "Golf" in sport:
						period_tree = sport_str.get('period')
						for period_str in period_tree:
							period = period_str.get('period')
							default = period_str.get('isdefault')
							label = period_str.get('label').strip("#1234567890 ")
							if default:
								currperiod = int(period)
								currlabel = label
			
			f = urllib2.urlopen(URL % (leaguename, currperiod))
			jsonp = f.read()
			f.close()
			json_str = jsonp.replace(\
					'shsMSNBCTicker.loadGamesData(', '').replace(');', '')
			json_parsed = json.loads(json_str)
			        
			for tour_str in json_parsed.get('games', []):
				tournament_tree = ET.XML(tour_str)
				tourname = tournament_tree.get('name').strip("#1234567890 ")
				tour_status = tournament_tree.get('status')
				curr_round = tournament_tree.get('curr-round')
				total_rounds = tournament_tree.get('rounds')

				header = 'PGA: ' + tourname+' Round '+curr_round+' (of '+total_rounds+'): '
				titlelen = len(header)
				if "Pre-Tourney" in tour_status:
					print 'PGA: '+ tourname+ ': No Rounds Scheduled Today'
				else:	
					for item in tournament_tree[:15]:
			 			if item <> 'tournament':			 			
			 				golfer_tree = item.find('golfer-one')
			 				gamestate_tree = item.find('gamestate')
			 				status = gamestate_tree.get('status')
			 				if "In-Progress" in status:
			 					status = gamestate_tree.get('display_status1')
			 				if "Pre-Round" in status:
			 					status = gamestate_tree.get('display_status1') + ' Tee'
			 				golfer = golfer_tree.get('alias').strip("#1234567890 ")
			 				tourn_score = golfer_tree.get('score')
			 				position = golfer_tree.get('place')

							round_scores = '('

							for score_item in golfer_tree:
								score_tree = score_item
								head = score_tree.get('heading')
						
								temp = score_tree.get('value')
								if temp == '':
									temp = ''
								if head == 	'T':	
									round_scores = round_scores + ')'
								elif head == '1':
									round_scores = round_scores + str(temp)
								elif temp <> '':
									round_scores = round_scores +','+str(temp)											

							# output	
						
							print header+ '<br>'+ position +'- ' +golfer+' ('+status+')   ' + round_scores+';'
						
							
		except Exception, e:
			print e
			time.sleep(5)
			continue
		break
		
	return sports
#-------------------------------------------------------------------------------
# Standard Schedule/Scores Pull

def today(league):
    
    SportsInfoURL = "http://scores.nbcsports.msnbc.com/ticker/data/sports.js.asp?jsonp=true&sport=%s&period=%d"
    yyyymmdd = int(datetime.datetime.now(\
    pytz.timezone('US/Eastern')).strftime("%Y%m%d"))
    date = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%D")
    
    if league == "CFB" or league == "NFL":
		f = urllib2.urlopen(SportsInfoURL % (league, yyyymmdd))
		jsonp = f.read()
		f.close()
		json_str = jsonp.replace('shsMSNBCTicker.loadSportsData(', '').replace(');', '')
		json_parsed = json.loads(json_str)
			
		#for sport_str in json_parsed.get('sport',[]):
		for sport_str in json_parsed:
				sport = sport_str.get('sport').strip("#1234567890 ")
				if league in sport:
					period_tree = sport_str.get('period')
					for period_str in period_tree:
						period = period_str.get('period')
						default = period_str.get('isdefault')
						label = period_str.get('label').strip("#1234567890 ")
						if default:
							currperiod = int(period)
							currlabel = label

    games = []
    max_attempts = 3

    for attempt in range(max_attempts):
		try:
			if league == "CFB" or league == "NFL":
				f = urllib2.urlopen(URL % (league, currperiod))
			else:
				f = urllib2.urlopen(URL % (league, yyyymmdd))
			jsonp = f.read()
			f.close()
			json_str = jsonp.replace(\
				'shsMSNBCTicker.loadGamesData(', '').replace(');', '')
			json_parsed = json.loads(json_str)

			count = 0
			for game_str in json_parsed.get('games',[]):
				count=count + 1
			if count == 0:
				print league + ': No Games Scheduled Today;'	
			if count > 0: 
				for game_str in json_parsed.get('games', []):
					game_tree = ET.XML(game_str)
					visiting_tree = game_tree.find('visiting-team')
					home_tree = game_tree.find('home-team')
					gamestate_tree = game_tree.find('gamestate')
					if league == "CFB":
						home = home_tree.get('alias')
						away = visiting_tree.get('alias')

					else:
						home = home_tree.get('alias').strip("#1234567890 ")
						away = visiting_tree.get('alias').strip("#1234567890 ")
						
					game_start = int(time.mktime(time.strptime(\
						'%s %d' % (gamestate_tree.get('gametime'), yyyymmdd),\
						'%I:%M %p %Y%m%d')))
					start = datetime.datetime.fromtimestamp(\
						game_start,
						pytz.timezone('US/Eastern')).strftime('%I:%M %p')
								
					if "In-Progress" in gamestate_tree.get('status'):
						print league+': '+home+': '+home_tree.get('score').rstrip()+' '+away+': '+visiting_tree.get('score')+' ('+gamestate_tree.get('display_status1')+' '+gamestate_tree.get('display_status2')+');'
					if "Final" in gamestate_tree.get('status'):
						print league+': '+home+': '+home_tree.get('score').rstrip()+' '+away+': '+visiting_tree.get('score')+' ('+gamestate_tree.get('display_status1')+');'
					if "Pre-Game" in gamestate_tree.get('status'):	
						print league+': '+home+' '+away+' '+gamestate_tree.get('status')+' ('+gamestate_tree.get('display_status1')+');'

		except Exception, e:
			print e
			time.sleep(5)
			continue
		break

    return games
#-------------------------------------------------------------------------------

# Available Leagues: 'MLB','NFL', 'PGA','NHL','CFB', 'NASCAR' (not handled, may be like golf?),
#					 'MLS', 'EPL', 'WORLDCUP','NBA', 'CBK', 'TOUR', 'FORM1'
#
# List of available leagues may change at "http://scores.nbcsports.msnbc.com/ticker/data/sports.js.asp"

for league in ['NFL', 'CFB', 'PGA', 'MLB', 'NHL']:
   	if "PGA" in league:
   		golf(league)
   	else:
   		today(league)	
#===============================================================================
