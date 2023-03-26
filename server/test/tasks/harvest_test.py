import server.tasks.harvest as harvest

def test_createHarvest():
  t = harvest.Harvest(0, {}, None)
  assert t is not None

def test_createHarvestTransport():
  t = harvest.HarvestTransport(0, {}, {})
  assert t is not None