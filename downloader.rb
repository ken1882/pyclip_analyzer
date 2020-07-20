# OilyDignifiedPoxDansGame
# AdventurousCharmingBoarTakeNRG
# SmilingConcernedSlothShazBotstix
# CulturedSpikyDragonRedCoat
# ElatedManlySkunkPRChase

clips = %w(
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
)

clips.each do |clip|
	cmd = "python3 sample_automata.py -c #{clip} -y"
	puts cmd
	system(cmd)
end