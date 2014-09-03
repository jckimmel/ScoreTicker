command: 'python ScoreTicker/score_ticker.py'

refreshFrequency: 30000

style: """
	position: absolute
	top: 0%
	left: 40%
	color: #000
	font-family: Arial Black
	
	.output, .ticker
		padding 5px 10px
		width: 1500px
		font-size: 28px
		font-weight: lighter
			font-smoothing: antialiased		
    	
"""

render: (output) -> """
	<div class="output">
		Current Scores:
		<div class="ticker"></div>
	</div>
	"""

update: (output, domEl) ->
	
	dom = $(domEl)
	tickerEl = $(domEl).find 'ticker'
	
	# parse each line of the output, based on the ";" at the end.
	games = output.split(';')
	numGames= games.length
		
	#stop previous timer, if any
	clearInterval @tickerInterval if @tickerInterval
	
	#install new timer
	currentIdx = 0
	@tickerInterval = setInterval ->
		#start from beginning again if we reached the end
		currentIdx = 0 if currentIdx >= numGames
		#tickerEl.html games[currentIdx]
		dom.find('.ticker').html games[currentIdx].toUpperCase() 
		currentIdx++
	,   10000 # 10 seconds