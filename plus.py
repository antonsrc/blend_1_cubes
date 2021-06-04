import os

file_list = os.listdir(path = "D:\\py\\out")

count_arr = ['0']*201
for i in range(len(file_list)):
    f_ = str(file_list[i])
    f_ = f_[:-4].split(' ')
    f = int(f_[0])
    # count_arr[f] += 1
    count_arr[f] = str(int(count_arr[f]) + 1)

for i in range(len(count_arr)):
    count_arr[i] = count_arr[i] + '_' + str(i)
    
count_arr.sort()

print('\n'.join(count_arr))
