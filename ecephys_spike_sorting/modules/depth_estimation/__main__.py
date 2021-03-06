from argschema import ArgSchemaParser
import os
import logging
import time

import numpy as np

from .depth_estimation import compute_offset_and_surface_channel
from ...common.utils import write_probe_json


def run_depth_estimation(args):

    print('ecephys spike sorting: depth estimation module')

    start = time.time()

    numChannels = args['ephys_params']['num_channels']

    rawDataAp = np.memmap(args['ephys_params']['ap_band_file'], dtype='int16', mode='r')
    dataAp = np.reshape(rawDataAp, (int(rawDataAp.size/numChannels), numChannels))

    rawDataLfp = np.memmap(args['ephys_params']['lfp_band_file'], dtype='int16', mode='r')
    dataLfp = np.reshape(rawDataLfp, (int(rawDataLfp.size/numChannels), numChannels))

    info = compute_offset_and_surface_channel(dataAp, dataLfp, \
           args['ephys_params'], args['depth_estimation_params'])

    write_probe_json(args['common_files']['probe_json'], info['channels'], info['offsets'], \
        info['scaling'], info['mask'], info['surface_channel'], info['air_channel'], info['vertical_pos'], info['horizontal_pos'])

    execution_time = time.time() - start

    print('total time: ' + str(np.around(execution_time,2)) + ' seconds')
    print()
        
    return {"surface_channel": info['surface_channel'],
            "air_channel": info['air_channel'],
            "probe_json": args['common_files']['probe_json'],
            "execution_time": execution_time} # output manifest

def main():

    from ._schemas import InputParameters, OutputParameters

    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = run_depth_estimation(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
