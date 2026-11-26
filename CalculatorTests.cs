using Microsoft.VisualStudio.TestTools.UnitTesting;
using System;
using System.Collections.Generic;

namespace CalculatorApp.Tests
{
    [TestClass]
    public class CalculatorTests
    {
        #region CalculateTotal Tests

        [TestMethod]
        public void CalculateTotal_MitNormalenPreisen_LiefertKorrekteSumme()
        {
            // Arrange
            var prices = new List<double> { 10.5, 20.3, 5.2 };

            // Act
            double result = Calculator.CalculateTotal(prices);

            // Assert
            Assert.AreEqual(36.0, result, 0.001);
        }

        [TestMethod]
        public void CalculateTotal_MitEinemPreis_LiefertDiesenPreis()
        {
            // Arrange
            var prices = new List<double> { 42.0 };

            // Act
            double result = Calculator.CalculateTotal(prices);

            // Assert
            Assert.AreEqual(42.0, result);
        }

        [TestMethod]
        public void CalculateTotal_MitLeererListe_LiefertNull()
        {
            // Arrange
            var prices = new List<double>();

            // Act
            double result = Calculator.CalculateTotal(prices);

            // Assert
            Assert.AreEqual(0.0, result);
        }

        [TestMethod]
        public void CalculateTotal_MitNullListe_WirftArgumentNullException()
        {
            // Arrange
            List<double> prices = null;

            // Act & Assert
            Assert.ThrowsException<ArgumentNullException>(() => Calculator.CalculateTotal(prices));
        }

        [TestMethod]
        public void CalculateTotal_MitNegativemPreis_WirftArgumentException()
        {
            // Arrange
            var prices = new List<double> { 10.0, -5.0, 3.0 };

            // Act & Assert
            Assert.ThrowsException<ArgumentException>(() => Calculator.CalculateTotal(prices));
        }

        [TestMethod]
        public void CalculateTotal_MitGanzzahlen_LiefertKorrekteSumme()
        {
            // Arrange
            var prices = new List<double> { 1, 2, 3, 4, 5 };

            // Act
            double result = Calculator.CalculateTotal(prices);

            // Assert
            Assert.AreEqual(15.0, result);
        }

        [TestMethod]
        public void CalculateTotal_MitNullPreisen_LiefertKorrekteSumme()
        {
            // Arrange
            var prices = new List<double> { 0.0, 0.0, 0.0 };

            // Act
            double result = Calculator.CalculateTotal(prices);

            // Assert
            Assert.AreEqual(0.0, result);
        }

        #endregion

        #region Divide Tests

        [TestMethod]
        public void Divide_MitNormalenWerten_LiefertKorrektesErgebnis()
        {
            // Arrange & Act
            double result = Calculator.Divide(10.0, 2.0);

            // Assert
            Assert.AreEqual(5.0, result);
        }

        [TestMethod]
        public void Divide_MitFließkommazahlen_LiefertKorrektesErgebnis()
        {
            // Arrange & Act
            double result = Calculator.Divide(7.5, 2.5);

            // Assert
            Assert.AreEqual(3.0, result);
        }

        [TestMethod]
        public void Divide_MitNegativenZahlen_LiefertKorrektesErgebnis()
        {
            // Arrange & Act
            double result = Calculator.Divide(-10.0, 2.0);

            // Assert
            Assert.AreEqual(-5.0, result);
        }

        [TestMethod]
        public void Divide_MitBeidenNegativenZahlen_LiefertKorrektesErgebnis()
        {
            // Arrange & Act
            double result = Calculator.Divide(-10.0, -2.0);

            // Assert
            Assert.AreEqual(5.0, result);
        }

        [TestMethod]
        public void Divide_DurchNull_WirftDivideByZeroException()
        {
            // Act & Assert
            Assert.ThrowsException<DivideByZeroException>(() => Calculator.Divide(10.0, 0.0));
        }

        [TestMethod]
        public void Divide_MitGanzzahlen_LiefertKorrektesErgebnis()
        {
            // Arrange & Act
            double result = Calculator.Divide(20, 4);

            // Assert
            Assert.AreEqual(5.0, result);
        }

        [TestMethod]
        public void Divide_Mit1AlsTeiler_LiefertDenZahler()
        {
            // Arrange & Act
            double result = Calculator.Divide(42.0, 1.0);

            // Assert
            Assert.AreEqual(42.0, result);
        }

        #endregion
    }
}
