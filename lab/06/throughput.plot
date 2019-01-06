set xlabel "time [s]"
set ylabel "Throughput [packets/sec]"
set key bel
plot "tcp1.tr" t "Throughput_tcp1" w lp lt rgb "blue", "tcp2.tr" u ($1):($2) t "Throughput_tcp2" w lp lt rgb "red"
pause -1
