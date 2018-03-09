class RatiosManager:
    def __init__(self, sampling_time, ratios_sampling_time, ratios_time_length):
        self.sampling_time = sampling_time
        self.ratios_time_length = ratios_time_length
        self.add_ratio_period = int(ratios_sampling_time / self.sampling_time)
        self.ratios = []
        self.index = 0

        sampling_time_minutes = self.sampling_time / 60
        ratios_minutes = self.ratios_time_length * 60
        self.list_length = int(ratios_minutes / sampling_time_minutes)

    def add_ratio(self, ratio):
        if self.index == self.add_ratio_period:
            self.index = 0
            self.ratios.append(ratio)

            if len(self.ratios) > self.list_length:
                del self.ratios[0]
        
        self.index += 1

    def average_ratio(self):
        return sum(self.ratios) / float(len(self.ratios))

    def is_list_full(self):
        return len(self.ratios) == self.list_length
