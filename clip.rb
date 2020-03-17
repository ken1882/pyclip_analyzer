
Strip = 30

def clip_cmd(st_time, idx)  
  cmd = sprintf("ffmpeg -ss %d -t #{Strip} -i livestream.mp3 sample/livestream_tmp%03d.mp3", st_time, idx)
  system(cmd)
end

slices = 10
slices.times do |i|
  clip_cmd((i + 1) * Strip, i)
end