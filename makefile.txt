README:

1)The program was developed and tested on Windows OS
2)The program was developed using python 3.6.3

Steps to start server:
1)In the command prompt, start the server by 'python p2mpserver.py 7735 [filename.txt] [probability factor]'

Please note that the probability factor should be in the range of 0 to 1

Steps to start client:
1)In the command prompt, start the client by 'python p2mpclient.py [IP address of server1] [IP address of server2] 7735 [filename.txt] [MSS]'
MSS with values till 2000 has been tested on this code.

Testing:
File size of 11.4MB has been used for testing

Task 1 - Effect of number of servers:
Keeping MSS and probability loss factor constant, the number of servers has been varied
MSS - 500
Probability loss ratio, p - 0.05
Number of servers, n - 1,2,3,4,5

Task 2 - Effect of MSS:
Keeping number of servers and probability loss ratio constant, the number of servers has been varied
MSS - 100,200,300,400,500,600,700,800,900,1000
Probability loss ratio, p - 0.05
Number of servers, n - 3

Task 2 - Effect of probability loss factor:
Keeping number of servers and MSS constant, the number of servers has been varied
MSS - 500
Probability loss ratio, p - 0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1
Number of servers, n - 3

