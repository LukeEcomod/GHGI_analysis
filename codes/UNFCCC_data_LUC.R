
library(readxl)
library(dplyr)
library(tidyr)
library(ggplot2)
library(stringr)

# COLORS 
library(ggsci)
library(scales)

# Get 10 colors from NPG palette
npg_colors <- pal_npg("nrc")(10)

# Repeat colors to cover 23 groups
colors_for_24 <- rep(npg_colors, length.out = 24)

# Check the colors visually
show_col(colors_for_24)


# Path to Excel file
file_path <- "../sheets/GHGinv2025_all_countries_Table4.1_Land_Transition_Matrix_1990_2023_20260109.xlsx"

# Get all sheet names
sheet_names <- excel_sheets(file_path)

#### COUNTRIES TO include

EUplus500 <-  c("AUT","BEL","BGR","CHE","CZE","DEU","DNK","ESP","EST","FIN","FRA","GRC","HRV","IRL","ITA","LTU","LVA","POL","PRT","ROU","SVK","SVN","SWE","NOR","UK", "EU")

# Filter sheets that represent conversions TO forest land (managed or unmanaged)
# 
# forest_sheets <- sheet_names[grepl("->FL", sheet_names)  & !grepl("^FL", sheet_names)]
# Metsä + metsitys
#forest_sheets <- sheet_names[grepl("->FL", sheet_names) | grepl("FL", sheet_names)]

#metsäkato
forest_sheets  <- sheet_names %>%
  # Keep only those starting with FL
  .[str_detect(., "^FL\\(.*\\)->")] %>%
  # Remove those where destination also starts with FL
  .[!str_detect(., "->FL\\(")]

# Read and process each sheet
forest_data_list <- lapply(forest_sheets, function(sheet) {
  df <- read_excel(file_path, sheet = sheet)
  colnames(df)[1] <- "Country"
  df_long <- df %>%
    pivot_longer(cols = -Country, names_to = "Year", values_to = "Value") %>%
    mutate(Year = as.integer(Year),
           Value = suppressWarnings(as.numeric(Value)),
           ConversionType = sheet)
  df_long <- df_long %>% filter(!is.na(Value))
  df_long
})

# Combine all forest-related conversions
combined_forest_data <- bind_rows(forest_data_list)

# Aggregate by Country and Year

forest_summary_country <- combined_forest_data %>%
  group_by(Country, Year) %>%
  summarise(Total_Forest_Conversion = sum(Value, na.rm = TRUE), .groups = "drop")

forest_summary_country <- forest_summary_country %>%
  mutate(Country = recode(Country,"GBR" = "UK"))     

#FILTER
forest_summary_country <- forest_summary_country %>%
    filter(Country %in% EUplus500)
# Sum over all countries by Year
eu_summary <- forest_summary_country %>%
  group_by(Year) %>%
  summarise(Total_Forest_Conversion = sum(Total_Forest_Conversion, na.rm = TRUE)) %>%
  mutate(Country = "EU") %>%
  select(Country, Year, Total_Forest_Conversion)

# Combine with original data
forest_summary_with_eu <- bind_rows(forest_summary_country, eu_summary)

# Check result
head(forest_summary_with_eu)
tail(forest_summary_with_eu)

library(ggsci)
npg_colors <- pal_npg("nrc")(10)  # Get 10 colors from NPG palette
print(npg_colors)
scales::show_col(npg_colors)


# Plot time series by country
p <- ggplot(forest_summary_with_eu, aes(x = Year, y = Total_Forest_Conversion)) +
    # , color = Country)) +
  geom_line(size = 1.2, color=npg_colors[1]) +
      scale_color_manual(values = "blue") + # colors_for_24[1]) +
 # geom_point() +
  labs(title = "Annual deforestation by Country",
       x = "Year", y = "Annual deforestation (1000 ha)") +
  theme_minimal() +
  facet_wrap(~Country, scales = "free_y", ncol=4)  # Separate panels for each country

print(p)

ggsave(p, file="../figs/deforestation_supplement.pdf",device=pdf,
       width=18, height=18, unit = "cm")
ggsave(p, file="../figs/deforestation_supplement.png",   width=18, height=18, unit = "cm")


# Metsitys
affor_sheets  <- sheet_names %>%
    # Keep only those ending with ->FL(...)
  .[str_detect(., "->FL\\(")] %>%
  #   # Remove those starting with FL(...)
  .[!str_detect(., "^FL\\(")]


# Read and process each sheet
forest_data_list <- lapply(affor_sheets, function(sheet) {
  df <- read_excel(file_path, sheet = sheet)
  colnames(df)[1] <- "Country"
  df_long <- df %>%
    pivot_longer(cols = -Country, names_to = "Year", values_to = "Value") %>%
    mutate(Year = as.integer(Year),
           Value = suppressWarnings(as.numeric(Value)),
           ConversionType = sheet)
  df_long <- df_long %>% filter(!is.na(Value))
  df_long
})

# Combine all forest-related conversions
combined_forest_data <- bind_rows(forest_data_list)

# Aggregate by Country and Year

forest_summary_country <- combined_forest_data %>%
  group_by(Country, Year) %>%
  summarise(Total_Forest_Conversion = sum(Value, na.rm = TRUE), .groups = "drop")

forest_summary_country <- forest_summary_country %>%
  mutate(Country = recode(Country,"GBR" = "UK"))                          

#FILTER
forest_summary_country <- forest_summary_country %>%
    filter(Country %in% EUplus500)
# Sum over all countries by Year
eu_summary <- forest_summary_country %>%
  group_by(Year) %>%
  summarise(Total_Forest_Conversion = sum(Total_Forest_Conversion, na.rm = TRUE)) %>%
  mutate(Country = "EU") %>%
  select(Country, Year, Total_Forest_Conversion)

# Combine with original data
forest_summary_with_eu <- bind_rows(forest_summary_country, eu_summary)

# Check result
head(forest_summary_with_eu)
tail(forest_summary_with_eu)




# Plot time series by country
p1 <- ggplot(forest_summary_with_eu, aes(x = Year, y = Total_Forest_Conversion)) +
    # , color = Country)) +
  geom_line(size = 1.2, color=npg_colors[3]) +
      scale_color_manual(values = npg_colors[3]) + # colors_for_24[1]) +
 # geom_point() +
  labs(title = "Annual afforestation by Country",
       x = "Year", y = "Annual afforestation (1000 ha)") +
  theme_minimal() +
  facet_wrap(~Country, scales = "free_y", ncol=4)  # Separate panels for each country

print(p1)

ggsave(p1, file="../figs/afforestation_supplement.pdf",device=pdf,
       width=18, height=18, unit = "cm")
ggsave(p1, file="../figs/afforestation_supplement.png",   width=18, height=18, unit = "cm")

