"""A tool to analyze the behavior of apps and their compliance with defined security rules."""
import time


def main(rules_engine, cli_arg_parser, process_handler) -> int:
    """The main function.

    - Load and filter rules based on cli arguments
    - Attach to process
    - Periodically check compliance
    - Record output
    """
    # get rules to track using args
    try:
        active_rules = rules_engine.filter_rules(rules_engine.get_rules(), cli_arg_parser.get_rules_args())
        # Attach python to the process. Start the process if required.
        process = process_handler.attach_to_process(cli_arg_parser.get_process_args())

        process_interval = cli_arg_parser.get_interval_arg()
        time_limit = cli_arg_parser.get_time_limit_arg()
    except (InvalidCliErr) as err:
        print(err)
        return 1
    except (ProcessCreationErr, ProcessAttachmentErr) as err:
        print(err)
        return 1
    # begin analyzing process
    try:
        start = time.monotonic()
        while (time_limit is None or time_limit > time.monotonic() - start)\
                and process.is_alive():
            loop_start = time.monotonic()
            try:
                # Check if the process is violating any rules, record a message if so
                output = rules_engine.check_compliance(process, active_rules)
                # format the result to be human readable, and optionally save to file

                result = process_handler.process_compliance_output(output)
                print(result)


            except (ComplianceCheckErr, ProcessRuntimeErr, PermissionError, TransformationErr) as err:
                print(err)
            elapsed = time.monotonic() - loop_start
            time.sleep(max(0, process_interval - elapsed))

    except KeyboardInterrupt:
        #Do whatever i need to safely handle this
        # allow multiple interrupts? Daemon mode?
    finally:
        try:
            if cli_arg_parser.get_create_process_flag():
                # python created the process
                process.shutdown()
            else:
                # continue process, end python.
                process.detach()
        except ShutdownError as err:
            print(err)

    return 0


if __name__ == "__main__":
    rules_engine = RulesEngine()
    cli_arg_parser = CLI_ArgParser()
    process_handler = ProcessHandler()

    main(rules_engine, cli_arg_parser, process_handler)


