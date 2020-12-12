id_list = %{

}.split(/[\r\n]+/).select{|l| !l.strip.empty?}.collect{|i| i.strip}

WORKER_CNT = 1

def spawn_automata(id_list, worker_id=0)
	id_list.each do |id|
		cmd = "python3 vod_download_analyze.py -i #{id}"
		puts "[Worker #{worker_id}]: #{cmd}"
		system(cmd)
	end
end

if WORKER_CNT > 1
	n = id_list.size
	queues = Array.new(WORKER_CNT){|i| id_list[i*n/WORKER_CNT...(i+1)*n/WORKER_CNT]}
	threads = []
	WORKER_CNT.times do |i|
		threads << Thread.new{spawn_automata(queues[i], i)}.run
	end
	threads.each{|th| th.join}
else
	spawn_automata(id_list)
end
