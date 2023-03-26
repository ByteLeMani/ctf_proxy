import time
import src.utils as utils
import src.filter_modules as modules
import src.log as log
import src.service_process as service_process
import src.constants as constants
from multiprocessing import Process, Value


def main():
    config_obj = utils.getConfig(constants.CONFIG_PATH)

    services_names = [service.name for service in config_obj.services]
    modules.generate_module_files(services_names, constants.MODULES_PATH)

    log_dict = log.parse(constants.LOG_PATH)

    # store the number of blocked packets in a list of "shared variables" between processes
    n_packets = []

    if log_dict:
        for service_name in services_names:
            value = 0
            if service_name in log_dict:
                value = log_dict[service_name]
            n_packets.append(Value('i', value))
    else:
        for _ in range(len(services_names)):
            n_packets.append(Value('i', 0))

    processes = []
    for index, service in enumerate(config_obj.services):
        processes.append(Process(target=service_process.service_function, args=(
                service, config_obj.global_config, n_packets[index]))
            )

    for process in processes:
        process.start()

    while True:
        time.sleep(constants.LOG_REFRESH_TIME)
        try:
            log_dict = {}
            for index, service_name in enumerate(services_names):
                log_dict[service_name] = n_packets[index].value
            log.update(constants.LOG_PATH, log_dict)
        except KeyboardInterrupt:
            break
        except:
            print("Error in opening log file")
    for process in processes:
        process.join()


if __name__ == '__main__':
    main()
