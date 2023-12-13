import puyapy

class dappInsurance(puyapy.ARC4Contract):
  def __init__(self) -> None:
    self.analyst = puyapy.Global.zero_address()
    self.customer = puyapy.Global.zero_address()

    self.assetName = puyapy.Bytes()
    self.assetValue = puyapy.UInt64(0)
    self.assetType = puyapy.Bytes()
    self.assetDescription = puyapy.Bytes()
    self.assetStatus = puyapy.Bytes()
    self.analystComments = puyapy.Bytes()
    self.asaId = puyapy.UInt64(0)



  @puyapy.arc4.abimethod(create=True)
  def create(
    self, 
    analyst: puyapy.Account,
    customer: puyapy.Account
    ) -> None:
    self.analyst = analyst
    self.customer = customer
    self.assetStatus = puyapy.Bytes(b"none")

  @puyapy.arc4.abimethod()
  def registerAsset(
   self,
    assetName: puyapy.arc4.String,
    assetValue: puyapy.arc4.UInt64,
    assetType: puyapy.arc4.String,
    assetDescription: puyapy.arc4.String
    ) -> None:
    assert puyapy.Transaction.sender() == self.customer, "Only registered customer can register asset"
    self.assetName = assetName.decode()
    self.assetValue = assetValue.decode()
    self.assetType = assetType.decode()
    self.assetDescription = assetDescription.decode()
    self.assetStatus = puyapy.Bytes(b"requested") 
  
  @puyapy.arc4.abimethod()
  def reviewRequest(
    self,
    acceptance: puyapy.arc4.Bool,
    analystComments: puyapy.arc4.String
    ) -> None:
    assert puyapy.Transaction.sender() == self.analyst, "Only registered analyst can review request"
    assert not self.assetStatus == puyapy.Bytes(b"accepted"), "Asset already accepted"
    assert not self.assetStatus == puyapy.Bytes(b"insured"), "Asset already insured"
    self.analystComments = analystComments.decode()
    if acceptance:
      self.assetStatus = puyapy.Bytes(b"accepted")
      puyapy.CreateInnerTransaction.begin()
      puyapy.CreateInnerTransaction.set_type_enum(puyapy.TransactionType.AssetConfig)
      puyapy.CreateInnerTransaction.set_fee(puyapy.UInt64(0))
      puyapy.CreateInnerTransaction.set_config_asset_total(puyapy.UInt64(1))
      puyapy.CreateInnerTransaction.set_config_asset_decimals(puyapy.UInt64(0))
      puyapy.CreateInnerTransaction.set_config_asset_name(puyapy.Bytes(b"Insurance"))
      puyapy.CreateInnerTransaction.set_config_asset_unit_name(puyapy.Bytes(b"INS"))
      puyapy.CreateInnerTransaction.set_note(puyapy.Bytes(b"Token for the asset"))
      puyapy.CreateInnerTransaction.submit()
      self.asaId = puyapy.InnerTransaction.created_asset_id()
    else:
      self.assetStatus = puyapy.Bytes(b"rejected")

  @puyapy.arc4.abimethod()
  def receiveToken(
    self,
    asset: puyapy._reference.Asset
    ) -> None:
    assert puyapy.Transaction.sender() == self.customer, "Only registered customer can receive token"
    assert self.assetStatus == puyapy.Bytes(b"accepted"), "Asset not accepted"
    assert self.asaId == asset.asset_id, "ASA ID not matching"
    # Verify Txn and add optin txn as requirement
    puyapy.CreateInnerTransaction.begin()
    puyapy.CreateInnerTransaction.set_type_enum(puyapy.TransactionType.AssetTransfer)
    puyapy.CreateInnerTransaction.set_fee(puyapy.UInt64(0))
    puyapy.CreateInnerTransaction.set_asset_receiver(puyapy.Transaction.sender())
    puyapy.CreateInnerTransaction.set_xfer_asset(asset.asset_id)
    puyapy.CreateInnerTransaction.set_asset_amount(puyapy.UInt64(1))
    puyapy.CreateInnerTransaction.submit()
    self.assetStatus = puyapy.Bytes(b"insured")

  


  
