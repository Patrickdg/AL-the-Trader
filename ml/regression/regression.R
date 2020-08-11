
# Libraries ---------------------------------------------------------------
library(data.table)
library(forecast)
library(dplyr)
library(caret)
library(readr)

# Data Setup --------------------------------------------------------------
df <- list.files(path='ml/stock_data/stock_features', full.names = TRUE) %>% 
  lapply(read_csv) %>% 
  bind_rows %>%
  data.frame
names(df)[1] <- 'Index'

##TRAIN/TEST SPLIT
set.seed(1111)
train_ind <- createDataPartition(df[,'next_close'], times = 1, p = 0.85, list = FALSE)
remove_cols <- c('Date','Index','sector','market_next_close_delta', 'next_close')

train <- df[train_ind,]
train_y <- train['next_close']; train <- train[setdiff(names(train), remove_cols)]
test <- df[-train_ind,]
test_y <- test['next_close']; test <- test[setdiff(names(test), remove_cols)]

##Remove near zero variance features
nearzeros <- nearZeroVar(train)
train <- train[,-nearzeros]
test <- test[,-nearzeros]

##PRINCIPAL COMPONENT ANALYSIS
set.seed(1111)
preProc <- preProcess(train, method = "pca", thresh = 0.9)
trainPC <- predict(preProc, train)
testPC <- predict(preProc, test)

##MODELLING, FEATURE SELECTION
# fit model 
fitall <- lm(next_close ~ ., data = cbind(trainPC, train_y)) 
# extract p-values
pvals <- summary(fitall)$coefficients[,4] 
# extract coefficients 
coefs <- summary(fitall)$coefficients[,1] 

top <- data.frame(cbind(coefs, pvals)) 
top <- top[order(top[,2], decreasing = FALSE),]
top <- top[top$pvals <= 0.05, ]; top # select features <= 0.05 pval
features <- c(rownames(top))

train <- cbind(trainPC, train_y)
train <- train[!is.infinite(rowSums(train)),]

model <- lm(next_close ~ ., data = train)

# Predictions -------------------------------------------------------------
predictions <- predict(model, newdata = testPC)
# confusionMatrix(predictions, test['next_close'])

predicted = cbind(testPC, test_y, predictions)
write.csv(predicted,'predicted.csv')
