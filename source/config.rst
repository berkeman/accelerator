``Accelerator.conf``
====================

when exax server starts, it looks for a file named  ``accelerator.conf`` in these places...

Typically, the file is created using ``ax init`` but it is
straightforward to maintain it by hand.

It is composed of the following sections:



.. code-block::

  method packages:
      dev  auto-discover
      live
