# mocking the used hasing functions
def default_backend():
  return None


class hashes:

  def SHA256():
    return None

  def Hash(idk, backend):
    class Hash:
      def update(self, data):
        pass

      def finalize(self):
        return bytes("deadbeef", "utf-8")
    return Hash()
