library(XML)
library(tm)
library(dplyr)
library(xtable)
library(wordcloud)
library(RColorBrewer)

speechtext <- function(ymd) {
  sotu<-data.frame(matrix(nrow=1, ncol=3))
  colnames(sotu) = c("speechtext", "year", "date")
  for (i in 1:length(ymd)) {
    year<-substr(ymd[i], 1, 4)
    url<-paste0('http://stateoftheunion.onetwothree.net/texts/', ymd[i], '.html')
    
    doc.html = htmlTreeParse(url, useInternal = TRUE)
    doc.text = unlist(xpathApply(doc.html, '//p', xmlValue))
    
    doc.text = gsub('\\n', ' ', doc.text)
    doc.text = gsub('\\"', '', doc.text)
    
    doc.text = paste(doc.text, collapse = ' ')
    
    x<-data.frame(doc.text, year, ymd[i], stringsAsFactors = FALSE)
    names(x)<-c("speechtext", "year", "date")
    sotu<-rbind(sotu, x)
    sotu<-sotu[!is.na(sotu$speechtext), ]
  }
  
  return(sotu)
}

sotu<-speechtext(c("20080128","20160112"))

docs<-Corpus(VectorSource(sotu$speechtext)) %>%
  tm_map(removePunctuation) %>%
  tm_map(removeNumbers) %>%
  tm_map(tolower) %>%
  tm_map(removeWords, stopwords("english")) %>%
  tm_map(stripWhitespace) %>%
  tm_map(PlainTextDocument)

tdm<-TermDocumentMatrix(docs) %>%
  as.matrix()

colnames(tdm) <- c("Bush", "Obama")

head(tdm)

bushsotu<-as.matrix(tdm[, 1])
bushsotu<-as.matrix(bushsotu[order(bushsotu, decreasing=TRUE),])
head(bushsotu)

obamasotu<-as.matrix(tdm[, 2])
obamasotu<-as.matrix(obamasotu[order(obamasotu, decreasing=TRUE),])
head(obamasotu)

par(mfrow=c(1,1))
#comparison.cloud(tdm, random.order = FALSE, colors=c("indianred3", "lightsteelblue3"), title.size=2.5, max.words=400)
#wordcloud(rownames(bushsotu), bushsotu, min.freq=3, scale=c(5, .2), random.order=FALSE, random.color=FALSE, colors=c("indianred1","indianred2","indianred3","indianred"))
#wordcloud(rownames(obamasotu), obamasotu, min.freq=3, scale=c(5, .2), random.order=FALSE, random.color=FALSE, colors=c("lightsteelblue1","lightsteelblue2","lightsteelblue3","lightsteelblue"))
commonality.cloud(tdm, random.order=FALSE, scale=c(5, .5), colors=brewer.pal(4, "Dark2"), max.words=400)