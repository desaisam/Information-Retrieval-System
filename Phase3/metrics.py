def runMetrics():
    
    mapDict={}
    queries=[]
    qdDict={}
    run_types = []
    relevance_documents={}
    

    # Please change RunType.txt file to the path of the score files for each run
    # (processes only one run at a time).
    # Outputs/TFIDF.txt
    # Outputs/QLM.txt
    # Outputs/BM25.txt
    # Outputs/Lucene_scores.txt
    runContent = open("RunType.txt", "r")
    for eachline in runContent:
        eachline = eachline.split()
        run_types.append(eachline)
    runContent.close()

    # Opens cacm rel file and calculates relevant documents in file.
    # Stores to a mapping dictionary.
    cacmRelevance = open("cacm.rel.txt", "r")
    for eachline in cacmRelevance:
        lines = eachline.split()
        if (lines[0]) in relevance_documents:
            relevance_documents[lines[0]] = relevance_documents[lines[0]] + 1
        else:
            relevance_documents[lines[0]]=1
        mapDict[lines[0]+lines[2]]=lines[3]
    cacmRelevance.close()

    for run in run_types:
        # Metrics variables for calculating evaluation values
        # P@5, P@20, Precision, Recall, average precision, total relevance
        p5={}
        p20 = {}
        recall = {}
        precision = {}
        average_precision={}

        rel_sum={}
        relevant = {}
        retrieved = {}

        rr={}
        flag={}
        file_evaluation_flag={}

        # Opens new file storing Metrics for the run being assessed.
        run=str(run).replace('[',"").replace(']',"").replace('\'',"")
        outfile = open(run[:-4]+"Metrics.txt", "w")
        outfile.write("Query \t Document \t Ranking \t Relevant(YES/NO) \t Precision "
                      "\t\t\t\t\t\t Recall"+"\n")
        file = open(run, "r")

        for eachline in file:
            line = eachline.split()
            if not (line[0] in queries):
                queries.append(line[0])
            if line[0] in relevance_documents:
                if line[0] in qdDict:
                    qdDict[line[0]].append(line[2])
                else:
                    qdDict[line[0]] = [line[2]]
        

        for i, tokens in qdDict.items():
            p5[i]=0
            p20[i]=0
            recall[i] = 0
            precision[i] = 0
            average_precision[i] = 0

            relevant[i] = 0
            retrieved[i] = 0

            rr[i] = 0
            flag[i] = 0

            file_evaluation_flag[i]=False

        if i not in relevance_documents:
            file_evaluation_flag[i]=True
        for i, tokens in relevance_documents.items():
            rel_sum[i]=tokens
        # Computations for assessment values and relevance
        for i, tokens in qdDict.items():
            for token2 in tokens:
                retrieved[i]=retrieved[i]+1
                rn="NO"
                if (i + token2) in mapDict:
                    if flag[i]==0:
                        rr[i]=1/retrieved[i]
                        flag[i]=1
                    relevant[i] = relevant[i] + 1
                    rn = "YES"
                    average_precision[i]=average_precision[i]+float(relevant[i]) /float(retrieved[i])
                precision[i] = float(relevant[i]) /float(retrieved[i])
                recall[i] = float(relevant[i])/float(rel_sum[i])

                if retrieved[i]==5:
                    p5[i]=precision[i]
                if retrieved[i]==20:
                    p20[i]=precision[i]

                outfile.write(str(i)+"\t\t"+str(token2)+"\t\t"+str(retrieved[i])+"\t\t\t\t"+ str(rn)
                              +"\t\t\t\t"+ str(precision[i]).ljust(30)+str(recall[i])+"\n")

            outfile.write("P@5 on query: "+str(i)+" is: "+str(p5[i])+"\n")
            outfile.write("P@20 on query: " + str(i) + " is: " + str(p20[i])+"\n\n")

        outfile.close()
runMetrics()
