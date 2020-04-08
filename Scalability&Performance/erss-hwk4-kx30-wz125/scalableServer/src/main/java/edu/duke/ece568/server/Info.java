package edu.duke.ece568.server;

/**
 * This class stands for all info we need to collect to perform analysis.
 */
public class Info {
    int requestCnt;

    public Info(){
        resetInfo();
    }

    // copy constructor
    public Info(Info info){
        this.requestCnt = info.requestCnt;
    }

    public int getRequestCnt() {
        return requestCnt;
    }

    public void addRequestCnt(){
        this.requestCnt++;
    }

    /**
     * This function will reset all info.
     */
    public void resetInfo(){
        requestCnt = 0;
    }
}
