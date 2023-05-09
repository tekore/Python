import os,subprocess

def get_value(key, string):
    value = 'NONE'
    for line in string.split('\n'):
        if key in line:
            value = line.split(':')[1].strip()
    return value

with open('/proc/meminfo') as memory:
    memory_data = memory.read()
#Total Memory:
total_memory = get_value('MemTotal', memory_data)
total_memory = float(total_memory.replace(' kB', "")) * 10**-6
formatted_total_memory = "{:.2f}".format(total_memory)

#Memory Free:
memory_free = get_value('MemFree', memory_data)
memory_free = float(memory_free.replace(' kB', "")) * 10**-6
formatted_memory_free = "{:.2f}".format(memory_free)

#Memory_Used
mem_used = float(formatted_total_memory) - float(formatted_memory_free)
 
#Percentages
used_percentage = (float(mem_used) / float(formatted_total_memory)) * 100
formatted_used_percentage = "{:.0f}".format(used_percentage)

print("Total RAM:", formatted_total_memory + "GB")
print("Used RAM:", mem_used, "GB")
print("Available RAM:", formatted_memory_free + "GB")
print("RAM OK:", formatted_used_percentage + "%")
