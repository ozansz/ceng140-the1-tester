import json
import random
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT

EP = 1e-5

fives = lambda x: float("%.5f" % x)

class Tester(object):
    def __init__(self, dataset, executable_path, logger):
        self.dataset = dataset
        self.executable_path = executable_path
        self.logger = logger

    def start(self):
        for test in self.dataset:
            process = Popen([self.executable_path], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            res = process.communicate(input="{lbl} {d1} {d2} {d3}".format(lbl=self.dataset[test]["label"],
                d1=self.dataset[test]["d1"], d2=self.dataset[test]["d2"], d3=self.dataset[test]["d3"]).encode())[0]
           
            try:
                res = float(res[:-1])
            except Exception:
                self.logger(test, "\u001b[31;1mFAIL/EOUT\u001b[0m", "Non-float output: %s..." % res[:20])
                continue

            if abs(res - self.dataset[test]["output"]) > EP:
                self.logger(test, "\u001b[31;1mFAIL/RES\u001b[0m", "Expected: {}, got: {}".format(self.dataset[test]["output"], res))
            else:
                self.logger(test, "\u001b[32;1mSUCCESS\u001b[0m")

class TestDataset(object):
    FILE_EXTENSIONS = ["csv", "json"]
    
    def __init__(self, labels, executable_path, samples=50, **kwargs):
        self.labels = labels
        self.executable_path = executable_path
        self.samples = samples
        self.logger = None
        self.do_logging = False

        self.__ts = str(datetime.now().timestamp()).split(".")[0]
        self.data = None

        if "logging" in kwargs:
            self.logger = kwargs["logging"]["loggerfn"]
            self.do_logging = kwargs["logging"]["logging_enabled"]

    @staticmethod
    def _rand_rate():
        return float("%.5f" % (random.randrange(1, 10) / (100 * 12)))

    @staticmethod
    def _rand_mc():
        return random.randrange(1, 30) * 12

    @staticmethod
    def _rand_loan():
        return random.randrange(1000, 100000, 100)

    @staticmethod
    def _rand_payment():
        return random.randint(10000, 100000) / 100

    def _loginfo(self, msg, depth=None):
        if self.do_logging:
            self.logger(msg, message_depth=depth)

    def set_sample_count(self, sc):
        try:
            self.samples = int(sc)
            self._loginfo("Set sample size to %d" % int(sc))
        except:
            pass

    def generate(self):
        self._loginfo("Generating new dataset")

        samples = self.samples
        self.data = list()

        if self.labels["L"]:
            self._loginfo("Generating subset for loan...", 2)

            for _ in range(samples):
                _r = self._rand_rate()
                _n = self._rand_mc()
                _p = self._rand_payment()
                
                process = Popen([self.executable_path], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                
                _L = process.communicate(input="1 {n} {p} {r}".format(n=_n, p=_p, r=_r).encode())[0]
                _L = float(_L[:-1])

                self.data.append({
                    "label": "1",
                    "d1": _n,
                    "d2": _p,
                    "d3": _r,
                    "output": fives(_L)
                })

        if self.labels["p"]:
            self._loginfo("Generating subset for payment...", 2)

            for _ in range(samples):
                _r = self._rand_rate()
                _n = self._rand_mc()
                _L = self._rand_loan()
                
                process = Popen([self.executable_path], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                
                _p = process.communicate(input="3 {L} {n} {r}".format(L=_L, n=_n, r=_r).encode())[0]
                _p = float(_p[:-1])

                self.data.append({
                    "label": "3",
                    "d1": _L,
                    "d2": _n,
                    "d3": _r,
                    "output": fives(_p)
                })

        if self.labels["n"]:
            self._loginfo("Generating subset for month count...", 2)

            for _ in range(samples):
                _r = self._rand_rate()
                _n = self._rand_mc()
                _L = self._rand_loan()
                
                process = Popen([self.executable_path], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                
                _p = process.communicate(input="3 {L} {n} {r}".format(L=_L, n=_n, r=_r).encode())[0]
                _p = float(_p[:-1])

                self.data.append({
                    "label": "2",
                    "d1": _L,
                    "d2": fives(_p),
                    "d3": _r,
                    "output": _n
                })

        if self.labels["r"]:
            self._loginfo("Generating subset for rate...", 2)

            for _ in range(samples):
                _r = self._rand_rate()
                _n = self._rand_mc()
                _L = self._rand_loan()
                
                process = Popen([self.executable_path], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                
                _p = process.communicate(input="3 {L} {n} {r}".format(L=_L, n=_n, r=_r).encode())[0]
                _p = float(_p[:-1])

                self.data.append({
                    "label": "4",
                    "d1": _L,
                    "d2": _n,
                    "d3": fives(_p),
                    "output": _r
                })

        self._loginfo("Genetarion successful.")

    def save(self, ext="csv", custom_filename=None):
        if self.data is None:
            raise TestDataset.NoDataError("No test data generated")

        if ext not in TestDataset.FILE_EXTENSIONS:
            raise TestDataset.UnknownExtensionError("Extension %s is not supported or unknown" % ext)

        if custom_filename:
            filename = custom_filename
        else:
            filename = "dataset_{ts}.{ext}".format(ts=self.__ts, ext=ext)

        self._loginfo("Saving dataset as %s" % filename)

        if ext == "csv":
            with open(filename, "w") as fd:
                fd.write("test_id,label,d1,d2,d3,output\n")
                for chunk in self.data:
                    fd.write("{tid},{lbl},{v1},{v2},{v3},{out}\n".format(
                        tid=self.data.index(chunk)+1, lbl=chunk["label"],
                        v1=chunk["d1"], v2=chunk["d2"], v3=chunk["d3"],
                        out=chunk["output"]))

            self._loginfo("Saved dataset", 2)
            return True

        if ext == "json":
            json_data = dict()
            for chunk in self.data:
                json_data[str(self.data.index(chunk)+1)] = {
                    "label": chunk["label"],
                    "d1": chunk["d1"],
                    "d2": chunk["d2"],
                    "d3": chunk["d3"],
                    "output": chunk["output"]
                }

            with open(filename, "w") as fd:
                json.dump(json_data, fd)

            self._loginfo("Saved dataset", 2)
            return True

    class UnknownExtensionError(ValueError):
        def __init__(self, message):
            super().__init__(message)
        
    class NoDataError(ValueError):
        pass