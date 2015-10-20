class Req:
    @staticmethod
    def update_session_includes(filepaths):
        return {
            "tag":"RequestUpdateSession",
            "contents":
                [ { "tag": "RequestUpdateTargets",
                    "contents": {"tag": "TargetsInclude", "contents": filepaths }
                  }
                ]
            }

    @staticmethod
    def get_source_errors():
        return {"tag": "RequestGetSourceErrors", "contents":[]}

    @staticmethod
    def get_exp_types(exp_span):
        return { "tag": "RequestGetExpTypes", "contents": exp_span}

    @staticmethod
    def get_exp_info(exp_span):
        return { "tag": "RequestGetSpanInfo", "contents": exp_span}

    @staticmethod
    def get_autocompletion(filepath,prefix):
        return {
            "tag":"RequestGetAutocompletion",
            "contents": [
                    filepath,
                    prefix
                ]
            }
