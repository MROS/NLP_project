buf = []
File.open("data/train.txt", "r").each do |line|
    buf << line
end

buf.sort!{|a, b| a.split[2] <=> b.split[2]}

buf.each do |line|
  print line
end
