class RatiosManager:
    def __init__(self, sampling_time, ratios_time_length):
        self.sampling_time = sampling_time
        self.ratios_time_length = ratios_time_length
        self.ratios = []

        sampling_time_minutes = self.sampling_time / 60
        ratios_minutes = self.ratios_time_length * 60
        self.list_length = ratios_minutes / sampling_time_minutes

    def add_ratio(self, ratio):
        self.ratios.append(ratio)

        if self.is_list_full():
            del self.ratios[0]

    def average_ratio(self):
        return sum(self.ratios) / float(len(self.ratios))

    def is_list_full(self):
        return len(self.ratios) == self.list_length
