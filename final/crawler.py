from os.path import join
from urllib.error import URLError
from bs4 import BeautifulSoup, SoupStrainer
import urllib.request
import csv


class Crawler(object):

    def __init__(self):
        self.channels = []
        self.schedule = []

    def run(self):
        self.take_channels()
        self.clear_channel_list()
        self.print_channels()
        self.read_channel_index()
        self.print_schedule()
        self.write_2txt()

        return True

    def take_channels(self):
        website_file = urllib.request.urlopen("http://programtv.se.pl/archiwum-tv/")
        website_html = website_file.read()
        website_file.close()
        links = SoupStrainer('section', {'class': 'tvArch'})

        soup = BeautifulSoup(website_html, "html.parser", from_encoding='ANSI', parse_only=links)

        for element in soup.find_all():
            var = [element.get_text(), element.get('href')]
            self.channels.append(var)
        self.clear_channel_list()
        self.expand_channel_archive_links()
        return self.channels

    def clear_channel_list(self):
        self.channels = [i for i in self.channels if i[1] is not None]
        return self.channels

    def expand_channel_archive_links(self):
        for channel, i in zip(self.channels, range(len(self.channels))):
            channel[1] = "http://programtv.se.pl/" + channel[1]

    def get_archive_links(self, index): 
        arch_links = []
        website_file = None
        print("Getting archive links...")

        try:
            website_file = urllib.request.urlopen(
                self.channels[index][1]) 

        except URLError as e:
            print(self.channels[index][0] + " - unable to open channel archive: " + e.reason)

        website_html = website_file.read()
        website_file.close()
        links2 = SoupStrainer('td', {'class': 'archRight'})
        soup2 = BeautifulSoup(website_html, "html.parser", parse_only=links2)
        for element in soup2.find_all():
            var = element.get('href')
            arch_links.append(var)

        arch_links = [i for i in arch_links if i is not None]
        self.channels[index].append(arch_links)
        print(" Done, got" + str(len(arch_links)))
        return arch_links

    def print_archive_links(self, index):
        for link, i in zip(self.channels[index][2], range(len(self.channels[index][2]))):
            print(str(i) + ". " + link[-11:-1])

    def prep_links(self, channel_index):
        for link in self.channels[channel_index][2]:
            index = self.channels[channel_index][2].index(link)
            link = "http://programtv.se.pl/" + link
            self.channels[channel_index][2][index] = link

    def print_channels(self):
        for channel, i in zip(self.channels, range(len(self.channels))):
            print(str(i) + " " + channel[0] + " " + channel[1])

    def get_day(self, day_link, channel_index, date_index):
        day_schedule = []
        website_file = None
        
        try:
            website_file = urllib.request.urlopen(day_link)

        except URLError as e:
            print(self.channels[channel_index][0] + " " +
                  self.channels[channel_index][2][date_index] +
                  " - unable to open channel archive: " + e.reason)

        website_html = website_file.read()
        website_file.close()
        link3 = SoupStrainer('div', {'class': 'program-row'})
        soup3 = BeautifulSoup(website_html, "html.parser", from_encoding='ANSI', parse_only=link3)
        for element in soup3.find_all('div', {'class': 'program-row'}):
            info = element.get_text("\n", strip=True)
            infotab = info.split("\n")

            if len(infotab) == 6:  
                day_row = [self.channels[channel_index][0],
                           self.channels[channel_index][2][date_index][-11:-1],
                           infotab[1], infotab[3],
                           join(infotab[4], infotab[5])
                               .replace("/", " ")]
                print(day_row)
                day_schedule.append(day_row)

            elif len(infotab) == 5:
                day_row = [self.channels[channel_index][0],
                           self.channels[channel_index][2][date_index][-11:-1],
                           infotab[1],
                           infotab[3],
                           infotab[4]]
                print(day_row)
                day_schedule.append(day_row)

            else:
                day_row = [self.channels[channel_index][0],
                           self.channels[channel_index][2][date_index][-11:-1],
                           infotab[1],
                           infotab[2]]
                day_schedule.append(day_row)

        self.schedule.append(day_schedule)

    def read_channel_index(self):
        pick = int(input("enter channel number: "))
        if 0 <= pick < len(self.channels):
            print("elo")
            self.get_archive_links(pick)
            self.prep_links(pick)
            self.print_archive_links(pick)
            self.read_date_index(pick)
        else:
            print("channel number out of allowed range")

    def read_date_index(self, channel_index):
        date_index = int(input("enter date number: "))
        print("picked date num: " + str(date_index))

        day_number = int(input("enter number of days to download: "))
        print("picked date num: " + str(day_number))
        
        for day_offset in range(0, day_number):
            if 0 <= date_index + day_number < len(self.channels[channel_index][2]):
                self.get_day(self.channels[channel_index][2][date_index + day_offset],
                             channel_index,
                             date_index + day_offset)
            else:
                print("date index out of allowed range(exceeded)")
                return

    def print_schedule(self):
        for day in self.schedule:
            for row in day:
                print(row)

    def write_2csv(self):
        with open('names.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['CHANNEL', 'DATE', 'STARTHOUR', 'ENDHOUR', 'TITLE']
            writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames, )
            writer.writeheader()
            for day in self.schedule:
                for row in day:
                    writer.writerow({'CHANNEL': row[0],
                                     'DATE': row[1],
                                     'STARTHOUR': row[2],
                                     'ENDHOUR': row[3],
                                     'TITLE': row[4]})

    def write_2txt(self):
        print("saving to txt file...")
        with open("schedule.txt", "w", encoding='utf-8') as text_file:
            text_file.write("CHANNEL;DATE;STARTHOUR;ENDHOUR;TITLE\n")
            for day in self.schedule:
                for row in day:
                    text_file.write(row[0] + ";" + row[1] + ";" + row[2] + ":00" + ";" + row[3] + ":00" + ";" + row[4] + "\n") 
        print("done")


crw = Crawler().run()
