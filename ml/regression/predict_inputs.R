# ! /usr/bin/Rscript
# Libraries ---------------------------------------------------------------
library(data.table)
library(forecast)
library(dplyr)
library(caret)
library(readr)

# Load Variables ----------------------------------------------------------
load(file = 'ml/regression/lm_objects/excl_nearzerovar_cols.rda')
load(file = 'ml/regression/lm_objects/incl_var_cols.rda')
load(file = "ml/regression/lm_objects/pca_preproc.rda")
load(file = "ml/regression/lm_objects/top_features.rda")
load(file = "ml/regression/lm_objects/regression_model.rda")

# Data Setup --------------------------------------------------------------
date <- format(Sys.Date(), '%m-%d-%Y')
remove_cols <- c('Date','Index','sector', 'Ticker', 'next_close', 'next_close_2', 'next_close_3','next_close_5','next_close_10')
df <- read_csv(sprintf('ml/regression/lm_inputs/inputs/input_features_%s.csv', date))
## Convert all number columns to numeric
tickers <- df$Ticker
df[setdiff(names(df), remove_cols)] <- df[setdiff(names(df), remove_cols)] %>% mutate_all(as.numeric)
train <- df[setdiff(names(df), remove_cols)]

# Processing --------------------------------------------------------------
# Remove near zero variance features and only include non-NA variance cols
train <- train[setdiff(names(train), nearzeros)]
var_cols <- var_cols[1:(length(var_cols)-1)]
train <- train[,var_cols]

##PRINCIPAL COMPONENT ANALYSIS
trainPC <- predict(preProc, train)

##MODELLING, FEATURE SELECTION
train <- trainPC[features]
train <- train[!is.infinite(rowSums(train)),] # remove inf values 

# Predictions -------------------------------------------------------------
prediction <- predict(model, newdata = train)
prediction <- cbind(tickers, train, prediction)

write.csv(prediction,sprintf('ml/regression/lm_inputs/predictions/predicted_%s.csv', date))
