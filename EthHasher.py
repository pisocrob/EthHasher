import time
import json, requests
from bs4 import BeautifulSoup
import ssdeep
import re
import cPickle as pickle

#Data Analysis imports
import numpy as np
import sklearn.cluster
import distance
import nltk

#Visual imports
import matplotlib.pyplot as plt
from wordcloud import WordCloud


class contract:
    """Deals with collection of contract data from the Internet.

    Uses both eitherscan.io and etherchain.org due to certain features being required
    from each site."""
    def __init__(self):
        pass
    #gets addresses from first page of list of verified contracts from etherscan.io
    #waits 3 seconds between page requests to avoid spamming
    def get_address_list(self, page_no):
        """Acquires list of verified contracts from etherscan.io

        keyword arguments:
        page_no -- The integer of pages of verfied contract to operate on"""
        address_arr = []
        while (page_no > 0):
            url = "https://etherscan.io/contractsVerified/"+str(page_no)
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html5lib')
            table = soup.find('table')
            for td in table.find_all('td'):
                for address in td.find_all('a',href=True):
                    address_arr.append(address['href'])
            time.sleep(3)
            page_no-=1
        #takes substring to remove unnecessary characters from address strings
        address_arr = map(lambda x: x[9:-5], address_arr)
        return address_arr

    #requests contract info by address from etherchain.org
    #returns array of bytecode
    #waits 3 seconds between requests to avoid 'abusing' to service

    def get_names(self, address_arr):
        #dict with address as key
        name_dict = {}
        i = 1

        #contracts with internal TX have a differnt page structure
        #neeed to do error handling to parse page in a different way
        for address in address_arr:
            url = "https://etherscan.io/address/"+address
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html5lib')
            name = soup.findAll('table')[4].findAll('td')[1]
            print str(i)+" "+str(name)[5:-6]
            i += 1
            name_dict.update({address: str(name)[5:-6]})
        return name_dict
            

    def get_bytecode(self, address_arr):
        """Acquires the bytecode for contract addresses passed to it

        keyword arguments:
        address_arr -- Array consisting of strings of contract addresses"""
        contract_source_url = "https://etherchain.org/api/account/"
        address_code = []
        for address in address_arr:
            resp = requests.get(contract_source_url+address)
            account_details = json.loads(resp.text)
            bytecode = account_details['data'][0]['code']
            print bytecode
            address_code.append(bytecode)
            time.sleep(3)
        return address_code

    #returns array of bytecode hash
    def get_hashes(self, address_code):
        """Given array of contract bytecodes returns array of corresponding ssdeep (CTPH) hashes

        keyword arguments:
        address_code -- Array of bytecodes as strings"""
        hash_arr = map(lambda x: ssdeep.hash(x), address_code)
        return hash_arr

    #given arrays for address and hashes will return a dict with address as key
    def get_hash_dict(self, address_arr, hash_arr):
        """Creates a dict of addresses and hashes with address as key value

        keyword arguments:
        address_arr -- Array of contract addresses as strings
        hash_arr -- Array of conrisponding bytecode hashes as strings"""
        hash_dict = dict(zip(hash_arr, address_arr))
        return hash_dict



class read_write:
    """Reading and writing to files operations for data obtained"""

    def __init__(self):
        pass

    def addresses_to_file(self, address_arr):
        """Writes each address to a new line in a text file named 'address_list.txt'

        keyword arguments:
        address_arr -- Array of addresses as strings"""
        file = open("address_list.txt", "w")
        for address in address_arr:
            file.write(address+"\n")
        file.close()

    def addresses_from_file(self, file_name):
        """Reads an address per line from file into array

        keyword arguments:
        file_name -- name of file to be read from"""
        address_arr = []
        with open(file_name, "r") as file:
            address_arr = file.read().splitlines()
        return address_arr

    def bytecode_to_file(self, address_code):
        """Writes one contract's bytecode per line to file named 'bytecode_list.txt'

        keyword arguments:
        address_code -- Array of bytecodes as strings"""
        file = open("bytecode_list.txt", "w")
        for code in address_code:
            file.write(code+"\n")
        file.close()

    def bytecode_from_file(self, file_name):
        """Reads a contract's bytecode per line from file into array

        keyword arguments:
        file_name -- name of file to be read from"""
        address_code = []
        with open(file_name, "r") as file:
            address_code = file.read().splitlines()
        return address_code

    def hashes_to_file(self, hash_arr):
        """Writes the hash of a contract's bytecode per line to file named 'hash_list.txt'

        keyword arguments:
        hash_arr -- array of hashes of contract bytecode as strings"""
        file = open("hash_list.txt", "w")
        for each_hash in hash_arr:
            file.write(each_hash+"\n")
        file.close

    def hashes_from_file(self, file_name):
        """Reads a hash of a contract's bytecode per line from file into array"""
        hash_arr = []
        with open(file_name, "r") as file:
            hash_arr = file.read().splitlines()
        return hash_arr

    def name_dict_to_file(self, name_dict, json_opt):
        if json_opt == True:
            with open("name_dict.json", "w") as file:
                json.dump(name_dict, file)
        else:
            with open("name_dict.txt", "w") as file:
                for key, name in name_dict.iteritems():
                    file.write(key+" - "+name+"\n")

    def names_from_json(self):
        with open("name_dict.json", "r") as file:
            name_dict = json.load(file)

        return name_dict


    #removes lines from all three files for which no bytecode was returned
    #checks for the hash '3:3:3' which is the result of '0x' which is returned by the API
    #when no bytecode is returned
    def clean_data(self):
        """Checks for and removes data entries from files where no bytecode is available.

        Checks against the hash '3:3:3' which is the hash of 'x0' as returned but etherchain.org
        API when no bytecode is given. Removes corresponding lines from all three data files if
        hash is found.

        Writes the cleaned data to a new file corrisponding to the read file's name with '_clean.txt' appended"""
        #readers for each file
        h_list_reader = open("hash_list.txt", "r")
        a_list_reader = open("address_list.txt", "r")
        b_list_reader = open("bytecode_list.txt", "r")

        #writers for each file
        h_list_writer = open("hash_list_clean.txt" , "w")
        a_list_writer = open("address_list_clean.txt", "w")
        b_list_writer = open("bytecode_list_clean.txt", "w")
        while True:
            h_line = h_list_reader.readline()
            if not h_line:
                break
            else:
                #check might not function as intended if it is possible for '3:3:3' to appear inside a hash
                if '3:3:3' in h_line:
                    #h_list_reader.next()
                    a_list_reader.next()
                    b_list_reader.next()
                else:
                    h_list_writer.write(h_line)
                    a_list_writer.write(a_list_reader.next())
                    b_list_writer.write(b_list_reader.next())



class machine_learning:
    """Data mining operations for data from files.

    Warning: Data should be cleaned using EthHasher.read_write.clean_data() before using this class."""

    def __init__(self):
        pass

    #uses affinity propagation to enable use of leventshein distance instead of euclidean distance required by k-means
    def cluster(self):
        """Performs affinity propagation on bytecode hashes from file

        Expects file named 'hash_list_clean.txt' as generated by EthHasher.read_write.clean_data().
        WARNING: This function can take a long time to run due to the levenshtein distance being computed
        each time it is run."""
        rw = read_write()
        hashes = np.asarray(rw.hashes_from_file('hash_list_clean.txt'))
        with open('mean_distmatrix.pk1', "r") as file:
            lev_similarity = pickle.load(file)
        
        print "distance measurements complete"
        affprop = sklearn.cluster.AffinityPropagation(affinity="precomputed", damping=0.5, max_iter=5000)
        affprop.fit(lev_similarity)
        file = open("cluster_all_mean.txt", "w")
        i = 1
        for cluster_id in np.unique(affprop.labels_):
            exemplar = hashes[affprop.cluster_centers_indices_[cluster_id]]
            cluster = np.unique(hashes[np.nonzero(affprop.labels_ == cluster_id)])
            cluster_str = ", ".join(cluster)
            file.write(" - *%s:* %s" % (exemplar, cluster_str + "\n"))
            print "Clusters done: " + str(i)
            i +=1
        file.close()

    def cluster_count(self):
        """Counters the number of contracts in each cluster stored in the 'cluster.txt' file

        Returns an array of numbers corrisponding to the number of contracts per cluster"""
        clust_no_array = []
        no_array = []
        i = 0
        with open("cluster_all_mean.txt", "r") as file:
            cluster_array = file.read().splitlines()
        for cluster in cluster_array:
            clust_no_array.append(cluster.split(", "))
            no_array.append(len(clust_no_array[i]))
            i += 1
        return no_array

    def exemplar_list(self):
        """Returns an array of the exemplars for each cluster found in the 'cluster.txt' file"""
        cluster_arr = []
        exemplar_arr = []
        p = re.compile("\*.*\*")
        with open("cluster.txt", "r") as file:
            cluster_arr = file.read().splitlines()
        for line in cluster_arr:
            exemplar_line = p.findall(line)[0]
            exemplar_arr.append(exemplar_line[1:-1])
        return exemplar_arr
        
    #works for rating if based return of word_freq function
    def bar_graph_gen(self, cluster_nos):
        """Displays a bar graph of the the number of contracts per cluster.

        Keyword arguments:
        cluster_no -- array of numbers of contracts per cluster.

        N.B: Work in progress
        """
        ax = plt.subplot(111)
        width = 0.8
        bins = map(lambda x: x-width/2,range(1,len(cluster_nos)+1))
        ax.bar(bins, cluster_nos,width=width)
        #ax.set_xticks(map(lambda x: x, range(1,len(cluster_nos)+1)))
        #ax.set_xticklabels(exemplar_arr, rotation=45)
        #plt.hist(cluster_nos, bins=length)
        plt.show()


    def bar_graph_words(self, freq_list):
        labels, y = zip(*freq_list)

        x = [0]*len(y)

        for i in range(len(y)):
            x[i] = i+1

        plt.bar(x,y)
        plt.xticks(x, labels, rotation='vertical')
        plt.show()

        

    def get_cluster_arr(self):
        cluster_hash_arr = []
        rw = read_write()
        hash_arr = rw.hashes_from_file("hash_list_clean.txt")

        with open("cluster_all_mean.txt") as file:
            cluster_hash_arr = file.read().splitlines()
        
        cluster_hash_arr = map(lambda x: x.replace("- *", ""), cluster_hash_arr)
        cluster_hash_arr = map(lambda x: x.replace(":*", ","), cluster_hash_arr)
        cluster_hash_arr = map(lambda x: x.strip(), cluster_hash_arr)
        cluster_hash_arr = map(lambda x: x.split(", ",), cluster_hash_arr)

        return cluster_hash_arr

    def cluster_addresses(self):
        ct = contract()
        rw = read_write()
        cluster_arr = self.get_cluster_arr()
        hash_dict = ct.get_hash_dict(rw.addresses_from_file('address_list_clean.txt'), rw.hashes_from_file('hash_list_clean.txt'))

        for i, each in enumerate(cluster_arr):
            for k, x in enumerate(each):
                cluster_arr[i][k] = hash_dict[str(x)]

        return cluster_arr

    def name_set_freq(self, common):
        rw = read_write()
        name_dict = rw.names_from_json()
        name_list = [v for v in name_dict.values()]
        p = re.compile('(.)([A-Z][a-z]+)')
        p2 = re.compile(('([a-z0-9])([A-Z])'))

        name_list = map(lambda x: p.sub(r'\1 \2', x), name_list)
        name_list = map(lambda x: p2.sub(r'\1 \2', x).lower().replace("_", " ").replace("  ", " "), name_list)
        final_words = []
        for name in name_list:
            temp_arr = name.split(" ")
            for each in temp_arr:
                final_words.append(each)


        fd = nltk.FreqDist(final_words)
        return fd.most_common(common)

        #return final_words

    def cluster_names(self):
        rw = read_write()
        cluster_names = self.cluster_addresses()
        name_dict = rw.names_from_json()

        for i, clust in enumerate(cluster_names):
            for j, x in enumerate(clust):
                cluster_names[i][j] = name_dict[str(x)]

        return cluster_names


    def format_names(self, cluster_names):
        p = re.compile('(.)([A-Z][a-z]+)')
        p2 = re.compile(('([a-z0-9])([A-Z])'))
        name_words = [[""]] * len(cluster_names)
        for i, clust in enumerate(cluster_names):
            final_l = []
            for j, x in enumerate(clust):
                first = p.sub(r'\1 \2', cluster_names[i][j])
                final = p2.sub(r'\1 \2', first).lower().replace("_", " ").replace("  ", " ")
                final_l += final.split(" ")
            name_words[i] = final_l
        return name_words

    def clean_names(self, name_words):
        #set used for prepositions checks
        stopwords = set(('and', 'or', 'to', 'a', 'it'))
        
        clean_words = [[""]] * len(name_words)
        for i, clust in enumerate(name_words):
            name_l = []
            for j,x in enumerate(clust):
                if name_words[i][j] not in stopwords:
                    name_l.append(name_words[i][j])
            clean_words[i] = name_l

        return clean_words
                
    def word_freq(self, clean_words, c_len=1, cutoff=0):
        ratings = []
        for clust in clean_words:
            if len(clust) > c_len:
                fd = nltk.FreqDist(clust)
                clust_rating = 1 - float(fd.B()) / float(fd.N())
                if cutoff <= clust_rating:
                    print fd.most_common(4), " : ", fd.B(), " / ", fd.N() , ": ", clust_rating
                    ratings.append(clust_rating)
        return ratings        

    #returns one word cloud for each cluster passed to it
    def cloud_gen(self, name_words):
        for clust in name_words:
            clust_words = ""
            for x in clust:
                clust_words += x + " "
            wc = WordCloud().generate(clust_words)
            plt.imshow(wc)
            plt.axis("off")
            plt.show()

    def cloud_gen_simple(self, name_words):
        words = ""
        for name in name_words:
            words += name + " "
        wc = WordCloud().generate(words)
        plt.imshow(wc)
        plt.axis("off")
        plt.show()

    def scatter_graph_gen(self, clust_no, rating):
        x = clust_no
        y = rating
        plt.scatter(x, y)
        plt.ylabel("Freq. dist. score")
        plt.xlabel("No. of contracts per cluster")
        plt.show()