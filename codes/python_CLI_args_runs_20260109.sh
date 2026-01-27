python ./euco2hwp_gains_losses.py -s 1990 -e 2023 --amissingnoeua -d ../GHGinv2025/UNFCCC_GHG_2025/ > amissing_no_eua_hwp_gains_losses_output.dat
python ./euco2hwp.py -s 1990 -e 2023 --amissingnoeua -d ../GHGinv2025/UNFCCC_GHG_2025/ > amissing_no_eua_hwp_output.dat
python ./eurestoration.py -s 1990 -e 2023 --amissing -d ../GHGinv2025/UNFCCC_GHG_2025/ > amissing_restoration_output.dat
python ./eulandtransitionmatrix.py -s 1990 -e 2023 --amissing -d ../GHGinv2025/UNFCCC_GHG_2025/ > amissing_land_transition_matrix_output.dat