class RatiosManager:
    def __init__(self, sampling_time, ratios_time_length):
        self.sampling_time = sampling_time
        self.ratios_time_length = ratios_time_length
        self.ratios = []

    def add_ratio(self, ratio):
        self.ratios.append(ratio)
        sampling_time_minutes = self.sampling_time / 60
        ratios_minutes = self.ratios_time_length * 60

        if len(self.ratios) == ratios_minutes / sampling_time_minutes:
            del self.ratios[0]

    def average_ratio(self):
        return sum(self.ratios) / float(len(self.ratios))