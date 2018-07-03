from argschema import ArgSchemaParser
import os
import logging
import time

from ecephys_spike_sorting.modules.automerging.automerging import automerging

from ecephys_spike_sorting.common.utils import write_cluster_group_tsv, load_kilosort_data


def run_automerging(args):

    logging.info('Running automerging')
    
    start = time.time()
    
    spike_times, spike_clusters, amplitudes, templates, channel_map, clusterIDs, cluster_quality = \
        load_kilosort_data(args['directories']['kilosort_output_directory'], \
            args['ephys_params']['sample_rate'], \
            convert_to_seconds = True)
    
    spike_clusters, cluster_index, cluster_quality = automerging(spike_times, spike_clusters, clusterIDs, templates, args['automerging_params'])

    write_cluster_group_tsv(cluster_index, cluster_quality)
    np.save(os.path.join(args['directories']['kilosort_output_directory'], 'spike_clusters.npy'), spike_clusters)

    execution_time = time.time() - start
    
    return {"execution_time" : execution_time} # output manifest


def main():

    from _schemas import InputParameters, OutputParameters

    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = run_automerging(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
