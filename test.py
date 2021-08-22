import time
a = 10000
b = 5
c = 7.5
x = 0

start = time.time()
for i in range(a):
    x = c//1
end = time.time()
print(end-start)

start = time.time()

for i in range(a):
    x = int(c)
end = time.time()

print(end-start)