This folder is for simulating a particular market algorithm without actually having to risk assets. The particular algorithm used in each bot will be explained in the comment header of each bot.

Some limitations of the simulated program:

  Sell trades will immidiately be executed, and will not fail. In reality, the price will be set to attempt to avoid taker fees, and
  as such, will sometimes have to be cancelled if the market swings too quickly.
  
  Extroplating will be a PITA, as the chart data pulled from CE's API is unclear how it is modified with its given parameters.
