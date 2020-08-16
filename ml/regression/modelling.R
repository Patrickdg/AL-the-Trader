# Libraries ---------------------------------------------------------------
library(data.table)
library(forecast)
library(dplyr)
library(caret)
library(readr)

# Data Setup --------------------------------------------------------------
df <- list.files(path='ml/regression/lm_objects/training/feature_data', full.names = TRUE) %>% 
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

##Remove near zero variance features and only include non-NA variance cols
nearzeros <- nearZeroVar(train)
save(nearzeros, file = 'ml/regression/lm_objects/excl_nearzerovar_cols.rda')
train <- train[,-nearzeros]
test <- test[,-nearzeros]

vars <- sapply(train, var); var_cols <- names(na.omit(vars))
save(var_cols, file = 'ml/regression/lm_objects/incl_var_cols.rda')
train <- train[,var_cols]
test <- test[,var_cols]

##PRINCIPAL COMPONENT ANALYSIS
set.seed(1111)
preProc <- preProcess(train, method = "pca", thresh = 0.9)
save(preProc, file = "ml/regression/lm_objects/pca_preproc.rda")

trainPC <- predict(preProc, train)
testPC <- predict(preProc, test)

##MODELLING, FEATURE SELECTION
# fit model 
fitall <- lm(next_close ~ ., data = cbind(trainPC, train_y)) 
# extract p-values
pvals <- summary(fitall)$coefficients[,4] 
# extract coefficients 
coefs <- summary(fitall)$coefficients[,1] 

# extract top features, p-val <= 0.05
top <- data.frame(cbind(coefs, pvals)) 
top <- top[order(top[,2], decreasing = FALSE),]
top <- top[top$pvals <= 0.05, ]; top
features <- c(rownames(top)); features <- features[-1] # remove 'intercept', 1st feature
save(features, file = "ml/regression/lm_objects/top_features.rda")

train <- trainPC[features]; test <- testPC[features]
train <- cbind(train, train_y); test <- cbind(test)
train <- train[!is.infinite(rowSums(train)),]

model <- lm(next_close ~ ., data = train)
save(model, file = "ml/regression/lm_objects/regression_model.rda")

# Predictions -------------------------------------------------------------
predictions <- predict(model, newdata = test)
# confusionMatrix(predictions, test_y)

predicted = cbind(test, test_y, predictions)
write.csv(predicted,'ml/regression/training_predictions.csv')