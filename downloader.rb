clips = %w(
	OilyDignifiedPoxDansGame
	AdventurousCharmingBoarTakeNRG
	SmilingConcernedSlothShazBotstix
	CulturedSpikyDragonRedCoat
	ElatedManlySkunkPRChase
	ColdbloodedSuperPeafowlDoubleRainbow
	AgileResoluteLadiesTakeNRG
	BreakableHandsomeVampireChocolateRain
	EmpathicDelightfulFlamingoTTours
	ArtisticTardyOkapiTTours
	AssiduousViscousQueleaThisIsSparta
	InspiringElegantTortoiseTooSpicy
	PricklyBlatantWerewolfDendiFace
	ClumsyTangibleElkDogFace
	PluckyOilyShrimpResidentSleeper
	SecretiveLazyVelociraptorBCWarrior
	NimbleModernNuggetsLitFam
	KindAmorphousCrabsBudBlast
	ConcernedSmellyWaterKlappa
	PrettiestFamousStrawberryPeteZaroll
).select{|c| !c.strip.empty?}

WORKER_CNT = 2

def spawn_automata(_clips, worker_id=0)
	_clips.each do |clip|
		cmd = "python3 sample_automata.py -c #{clip} -y"
		puts "[Worker #{worker_id}]: #{cmd}"
		system(cmd)
	end
end

n = clips.size
queues = Array.new(WORKER_CNT){|i| clips[i*n/WORKER_CNT...(i+1)*n/WORKER_CNT]}
threads = []
WORKER_CNT.times do |i|
	threads << Thread.new{spawn_automata(queues[i], i)}.run
end
threads.each{|th| th.join}
