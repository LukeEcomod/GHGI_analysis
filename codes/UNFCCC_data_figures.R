#############
####
getwd()

### read in data
library("readxl")
library("dplyr")
library("forcats")
library("tidyr")
library("ggsci")
library("scales")
library("gridExtra")
library("cowplot")
library("ggplot2")

###################
### UNFCCC data, published spring 2025, starting with FL data 
###################

# Excel file is in /data folder

FL <- as.data.frame(read_excel("./../sheets/GHGinv2025_all_countries_Restoration_1990_2023_20260109.xlsx", sheet="Table4.A FL"))

colnames(FL) <- c("country", "Year","totarea","minsoil","orgsoil", "biomassgain", "biomassloss", "biomasschange","DWchange","litterchange","minsoilchange","orgsoilchange","LBgain","LBloss","LBnet","DWnet","Lnet","MINnet","ORGnet","netco2")

# replacing NaN with NA
for (i in 1:dim(FL)[2]){   
FL[,i] <- ifelse(FL[,i]  %in% c("NaN"), NA, FL[,i] )
}
# converting numbers to numeric 
for (i in 2:dim(FL)[2]){   
FL[,i] <- as.numeric(FL[,i])
}
# Renaming GBR to UK
FL$country <- ifelse(FL$country=="GBR", "UK", FL$country)
FL$country <- ifelse(FL$country=="CHE", "CH", FL$country)


## data for whole EU, downloaded for EEA website 
## source: https://www.eea.europa.eu/en/analysis/publications/annual-european-union-greenhouse-gas-inventory-2025
## accessed 11.12.2025

EU <- as.data.frame(read_excel("./../sheets/EU_CRT_1990_2023.xlsx", sheet="Sheet1"))

colnames(EU) <- c("Year","totarea","minsoil","orgsoil", "biomassgain", "biomassloss", "biomasschange","DWchange","litterchange","minsoilchange","orgsoilchange","LBgain","LBloss","LBnet","DWnet","Lnet","MINnet","ORGnet","netco2","toHWP")

EU <-  EU %>%
    select(-toHWP) %>%
    mutate(country = "EU") %>%
    select(country, everything()) %>%
    mutate(biomasschange=LBnet/totarea) %>%
    mutate(biomassgain=NA, biomassloss=NA, DWchange=NA, litterchange=NA, minsoilchange=NA, orgsoilchange=NA) %>%
    mutate(Year=as.numeric(Year), biomassgain=as.numeric(biomassgain), biomassloss=as.numeric(biomassloss), DWchange=as.numeric(DWchange), litterchange=as.numeric(litterchange), minsoilchange=as.numeric(minsoilchange), orgsoilchange=as.numeric(orgsoilchange)) 

#### bind FL and European data frames

FL <- bind_rows(FL, EU)

## listing countries that have more than 500 kha of forests + EU + UK + NOR + CHE
EUplus500 <-  c("AUT","BEL","BGR","CH","CZE","DEU","DNK","ESP","EST","FIN","FRA","GRC","HRV","IRL","ITA","LTU","LVA","POL","PRT","ROU","SVK","SVN","SWE","NOR","UK", "EU")

FL2023 <- FL %>%
    filter(Year==2023) %>%
    filter(country %in% EUplus500)

# Listing sum for columns for EUplus500 countrues
colSums(FL2023[c("LBgain", "LBloss","LBnet","DWnet","Lnet","MINnet","ORGnet","netco2")], na.rm=TRUE)

FL <- FL %>%
        filter(country %in% EUplus500)

slope_data <- FL %>%
  group_by(country) %>%
  summarize(slope = coef(lm(biomasschange ~ Year))[["Year"]],
            x = 1990,            # x position for label
            y = 2)            # y position for label

slope_data <- slope_data %>%
  mutate(y = if_else(country == "IRL", -0.5, y))

# Create facet order from 2023 areas (largest to smallest)

facet_levels <- FL2023 %>%
  arrange(desc(totarea)) %>%
  pull(country)

FL2023 <- FL2023 %>%
  mutate(country = factor(country, levels = facet_levels))

# Apply ordering to both datasets used in the plot
FL <- FL %>%
  mutate(country = factor(country, levels = facet_levels))

slope_data <- slope_data %>%
  mutate(country = factor(country, levels = facet_levels))

npg_colors <- pal_npg("nrc")(10)  # Get 10 colors from NPG palette
print(npg_colors)
scales::show_col(npg_colors)

co2leg <- expression(paste("Tree biomass change, Mg CO"[2]," per ha", sep=" "))

p1 <- ggplot(data=FL, aes(x=Year, y=biomasschange)) +
    geom_line(color=npg_colors[4], linewidth = 1)+
    geom_smooth(method=lm, se=TRUE, linewidth=1.2, fullrange=TRUE, color = npg_colors[7]) +
    labs(y=co2leg) +   theme_bw() +
            theme(axis.text.x = element_text(size = 6)) +
    geom_hline(aes(yintercept=0), linetype=2) +
    ylim(-2,2.2) +
     geom_text(data=FL2023, aes(x=2010, y=-1.5, label=round((totarea), 0)), fontface = "italic", size = 4) +
    geom_text(data = slope_data, aes(x = 1990, y = y, label = paste0("Slope = ", round(slope, 3))),
            hjust = 0, vjust = 1, inherit.aes = FALSE, fontface = "italic", size = 2.5) +
                facet_wrap(~country, nrow=4)

p1

ggsave(p1, file="../figs/Figure1.pdf",device=pdf,
        width=18, height=12,  unit = "cm")

ggsave(p1, file="../figs/Figure1.png", width=18, height=12, unit = "cm")

#######################
### Figure 2

with_losses <- c("AUT","CZE","EST","FIN","FRA","HRV","ITA","LVA","PRT","ROU","SVK","SVN","UK")
## excluding Ireland, as its values are in different scale 

# 1) Reshape to long format
FL_long <- FL %>%
  select(country, Year, biomassgain, biomassloss, biomasschange) %>%
  filter(country %in% with_losses) %>%
  pivot_longer(
    cols = c(biomassgain, biomassloss, biomasschange),
    names_to = "variable",
    values_to = "value"
  )

# 2) Nice labels for legend
var_labels <- c(
  biomassgain   = "Biomass gain",
  biomassloss   = "Biomass loss",
  biomasschange = "Net change"
)

# 3) Colors (NPG palette)
npg_colors <- pal_npg("nrc")(10)
col_map <- c(
  biomassgain   = npg_colors[3],  # e.g., green
  biomassloss   = npg_colors[1],  # e.g., red
  biomasschange = npg_colors[4]   # e.g., blue
)

# 4) Linetypes (optional to enhance readability)
lt_map <- c(
  biomassgain   = "solid",
  biomassloss   = "solid",
  biomasschange = "solid"
)

# 5) Plot
co2leg2 <- expression(paste("Tree biomass (Mg CO"[2], " per ha)", sep = ""))

p2 <- ggplot(FL_long, aes(x = Year, y = value, color = variable, linetype = variable)) +
  geom_line(linewidth = 0.9, na.rm = TRUE) +
  scale_color_manual(values = col_map, labels = var_labels, name = NULL) +
  scale_linetype_manual(values = lt_map, labels = var_labels, name = NULL) +
  labs(y = co2leg2, x = NULL) +
  theme_bw() +
  theme(
    axis.text.x = element_text(size = 6),
    legend.position = "top",
    legend.title = element_blank()
  ) +
  geom_hline(yintercept = 0, linetype = 2) +
  coord_cartesian(ylim = c(-4, 4.5)) +
  facet_wrap(~ country, ncol = 4)

p2

ggsave(p2, file="../figs/Figure2.pdf",device=pdf,
        width=18, height=18,  unit = "cm")
ggsave(p2, file="../figs/Figure2.png", width=18, height=18, unit = "cm")

######
## Figure for biomass losses and HWP gains
######


hwpgains <-  as.data.frame(read_excel("./GHGinv2025_all_countries_no_EUA_Table4.Gs1_HWP_gains_losses_1990_2023_20260109.xlsx", sheet="Total HWP gains"))
colnames(hwpgains) <- c("row","country","Year","hwp_gains")

hwpgains$country <- ifelse(hwpgains$country=="GBR", "UK", hwpgains$country)

hwpgains <- hwpgains %>%
        filter(country %in% EUplus500)

FL_hwp <- FL %>%
    select(country, Year, totarea, biomassgain, biomassloss)

wrongunit <- c("TUR","BEL","ESP","FRA","GRC","PRT","NOR","SVK","SWE")

### countries with Living Biomass losses

LB_count <- c("AUT","CZE","EST","FIN","FRA","HRV","ITA","LVA","PRT","ROU","SVK","SVN","UK")

FL_hwp <- merge(FL_hwp, hwpgains) %>%
    mutate(hwp_gains=as.numeric(paste(hwp_gains))) %>%
    mutate(hwp_perha=(-3.6666*hwp_gains)/(totarea*1000)) %>%
    select(country, Year, biomassgain, biomassloss, hwp_perha) %>%
    mutate(hwp_perha= if_else(country %in% wrongunit, hwp_perha, 1000*hwp_perha)) %>%
    mutate(biomassloss=-as.numeric(paste(biomassloss))) %>%
    mutate(biomassloss=-1 * biomassloss)

fl.hwp.long <- gather(FL_hwp, type, sink, biomassgain:hwp_perha) %>%
    filter(type %in% c("biomassloss", "hwp_perha")) %>%
    mutate(sink=as.numeric(paste(sink))) %>%
    mutate(sink=-1*sink) %>% #removing countries that do not have LB losses 
    filter(country %in% with_losses)

yleg2 <- expression(paste("Biomass losses (Mg C per ha) and HWP gains (Mg CO"[2]," per ha) ", sep=" "))

# If you’re plotting fl.hwp.long:

present_levels <- intersect(facet_levels, unique(fl.hwp.long$country))
fl.hwp.long <- fl.hwp.long %>%
    mutate(country = fct_relevel(country, present_levels))

p3 <- ggplot(fl.hwp.long, aes(x=Year, y=sink, linetype=type, group=type)) +
 #       ylim(c(-7,0)) +
        ylab(yleg2) +
        geom_hline(aes(yintercept=0), linetype=2, color="gray") +
        geom_smooth(method=loess, se=TRUE, linewidth=1.2, fullrange=TRUE) +
        scale_color_manual(values = npg_colors[4]) +
        theme_bw() +
            theme(axis.text.x = element_text(size = 6)) +

        facet_wrap(~country, scales="free_y", ncol=4) +
    
    ggtitle("Forest land biomass losses (solid) & HWP gains (dashed), UNFCCC") +
        theme(legend.position="none") 

p3

ggsave(p3, file="../figs/Figure3.pdf",device=pdf,
      width=18, height=18, unit = "cm")
ggsave(p3, file="../figs/Figure3.png",  width=18, height=18, unit = "cm")

#################
### doing figrue 4
#################

# extending color palette for all countries
extended_colors <- rep(npg_colors, length.out = 20)  # for 20 groups

LBloss <- FL %>%
    select(country, Year, LBloss)

FL_hwp <- merge(FL_hwp, LBloss)

FL_hwp2 <-  FL_hwp %>%
    mutate(period = ifelse(Year<2009, "1990-2008", "2009-2017")) %>%
    mutate(period = ifelse(Year>2017, "2018-2023", period)) %>%
    group_by(country, period) %>%
    summarize(mean.gain = mean(biomassgain), mean.loss = mean(biomassloss), mean.hwp = mean(-1*hwp_perha), mean.totloss = mean(-1*LBloss)) %>%  ### NOTE converting HWP_perha and BMloss to positive
    filter(country %in% LB_count) %>%
    mutate(mean.hwp = mean.hwp / 3.66666)

##########

## modification of legends

co2legX <- expression(paste("Mean HWP inflow Mg C per ha", sep=" "))
co2legY <- expression(paste("Mean biomass loss Mg C per ha"))

# Common theme modification
theme_mod <- theme_bw() +  theme(axis.text = element_text(size = 10), axis.title = element_text(size = 8))  # Adjust font size here
              
p6 <- ggplot(data=FL_hwp2[FL_hwp2$period=="1990-2008",], aes(y=mean.loss, x=mean.hwp, color=country)) +
  geom_point(alpha=0.6, aes(size=mean.totloss)) +
     scale_size(range = c(2, 10), guide = "none") +
    # Removes bubble size legend
     scale_color_manual(values = extended_colors,
     guide = "none") +
    ylim(-4,0) +
    xlim(0, 0.7) +
    theme_mod +
    labs(y=co2legY, x=co2legX, size="Total biomass  \n losses", color="Country", title="1990-2008") +
    ggrepel::geom_text_repel(data = FL_hwp2[FL_hwp2$period=="1990-2008",], aes(label = country), show.legend = FALSE, max.overlaps = Inf)

p6

p7 <- ggplot(data=FL_hwp2[FL_hwp2$period=="2009-2017",], aes(y=mean.loss, x=mean.hwp, color=country)) +
  geom_point(alpha=0.6, aes(size=mean.totloss)) +
      scale_size(range = c(2, 10), guide = "none") +
    # Removes bubble size legend
     scale_color_manual(values = extended_colors,
     guide = "none") +
    ylim(-4,0) +
    xlim(0, 0.7) +
    theme_mod +
    labs(y=NULL, x=co2legX, size="Total biomass \n losses", color="Country", title="2009-2017") +
    ggrepel::geom_text_repel(data = FL_hwp2[FL_hwp2$period=="2009-2017",], aes(label = country), show.legend = FALSE, max.overlaps = Inf)

p7


p8 <- ggplot(data = FL_hwp2[FL_hwp2$period == "2018-2023",],aes(y = mean.loss, x = mean.hwp, color = country)) +
    geom_point(alpha = 0.6, aes(size = mean.totloss)) +
      scale_size(range=c(2,10)) +
    scale_color_manual(values = extended_colors,
    guide = guide_legend(override.aes = list(size=3, shape = 16))) +
    
    scale_size(range = c(2, 10), guide = "none") +
    # Removes bubble size legend
     scale_color_manual(values = extended_colors,
     guide = "none") +
    ylim(-4, 0) +
    xlim(0, 0.7) +
    theme_mod +
    labs(y = NULL, x = co2legX,color = "Country", title = "2018-2023") +
    ggrepel::geom_text_repel(data = FL_hwp2[FL_hwp2$period=="2018-2023",], aes(label = country), show.legend = FALSE, max.overlaps = Inf)
        
## Composite plot with equal widths
composite <- plot_grid(p6, p7, p8, nrow = 1, align = "v", rel_widths = c(1, 1, 1))

ggsave(composite, file="../figs/Figure4.pdf",device=pdf,
       width=18, height=12, unit = "cm")
ggsave(composite, file="../figs/Figure4.png",   width=18, height=12, unit = "cm")
