# Libraries ---------------------------------------------------------------
library(data.table)
library(forecast)
library(dplyr)
library(caret)
library(readr)

# Data Setup --------------------------------------------------------------
# df <- list.files(path='ml/stock_data/stock_features', full.names = TRUE) %>% 
#   lapply(read_csv) %>% 
#   bind_rows %>%
#   data.frame
# names(df)[1] <- 'Index'

# Remove unneeded columns
remove_cols <- c('Date','Index','sector','market_next_close_delta', 'next_close')
train <- train[setdiff(names(train), remove_cols)]

# Remove near zero variance features and only include non-NA variance cols
load(file = 'ml/regression/lm_objects/excl_nearzerovar_cols.rda')
train <- train[,-nearzeros]

load(file = 'ml/regression/lm_objects/incl_var_cols.rda')
train <- train[,var_cols]

##PRINCIPAL COMPONENT ANALYSIS
set.seed(1111)
load(file = "ml/regression/lm_objects/pca_preproc.rda")
trainPC <- predict(preProc, train)

##MODELLING, FEATURE SELECTION
load(file = "ml/regression/lm_objects/top_features.rda")

train <- trainPC[features]
train <- train[!is.infinite(rowSums(train)),] # remove inf values 

load(file = "ml/regression/lm_objects/regression_model.rda")

# Predictions -------------------------------------------------------------
prediction <- predict(model, newdata = train)

prediction <- cbind(train, prediction)
write.csv(prediction,'ml/regression/predicted.csv')
